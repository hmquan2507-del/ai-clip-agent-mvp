from __future__ import annotations

import json
import time
from dataclasses import dataclass

from google import genai
from google.genai import types

from app.core.config import settings

TRANSCRIPTION_MODEL = "gemini-2.5-flash"
FILE_ACTIVE_POLL_SECONDS = 2.0
FILE_ACTIVE_TIMEOUT_SECONDS = 120.0

TRANSCRIPTION_PROMPT = (
    "Transcribe the spoken audio in this video. Return ONLY a JSON array "
    "(no markdown fences, no commentary), where each item is "
    '{"start_seconds": number, "end_seconds": number, "text": string}, '
    "covering the entire spoken audio in the original spoken language. "
    "Keep each segment short (a single sentence or phrase, a few seconds "
    "long) so it reads well as a video subtitle. If there is no audible "
    "speech at all, return an empty array."
)


class GeminiTranscriptionError(RuntimeError):
    pass


@dataclass(frozen=True)
class TranscriptSegment:
    start_seconds: float
    end_seconds: float
    text: str


def transcribe_video(local_path: str) -> list[TranscriptSegment]:
    """Real speech-to-text via Gemini's native video understanding -
    replaces the rest of this codebase's hardcoded mock transcript
    providers (app/speech/whisper_provider.py, gemini_provider.py).

    Uploads the video through the Gemini Files API (required for anything
    beyond trivial inline size), waits for it to finish processing, then
    asks for a timestamped JSON transcript.
    """
    if not settings.gemini_api_key:
        raise GeminiTranscriptionError("GEMINI_API_KEY is not configured.")

    client = genai.Client(api_key=settings.gemini_api_key)

    uploaded = client.files.upload(file=local_path)

    deadline = time.monotonic() + FILE_ACTIVE_TIMEOUT_SECONDS
    file_info = uploaded
    while file_info.state == types.FileState.PROCESSING:
        if time.monotonic() > deadline:
            raise GeminiTranscriptionError(
                "Gemini file processing timed out before becoming active."
            )
        time.sleep(FILE_ACTIVE_POLL_SECONDS)
        file_info = client.files.get(name=uploaded.name)

    if file_info.state != types.FileState.ACTIVE:
        raise GeminiTranscriptionError(
            f"Gemini file upload failed: state={file_info.state}"
        )

    try:
        response = client.models.generate_content(
            model=TRANSCRIPTION_MODEL,
            contents=[file_info, TRANSCRIPTION_PROMPT],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.0,
            ),
        )
    finally:
        try:
            client.files.delete(name=uploaded.name)
        except Exception:
            pass

    if not response.text:
        raise GeminiTranscriptionError(
            "Gemini returned an empty transcription response."
        )

    try:
        raw_segments = json.loads(response.text)
    except json.JSONDecodeError as error:
        raise GeminiTranscriptionError(
            f"Gemini transcription response was not valid JSON: {error}"
        ) from error

    if not isinstance(raw_segments, list):
        raise GeminiTranscriptionError(
            "Gemini transcription response was not a JSON array."
        )

    segments: list[TranscriptSegment] = []
    for item in raw_segments:
        if not isinstance(item, dict):
            continue
        text = str(item.get("text", "")).strip()
        if not text:
            continue
        try:
            start_seconds = float(item["start_seconds"])
            end_seconds = float(item["end_seconds"])
        except (KeyError, TypeError, ValueError):
            continue
        if end_seconds <= start_seconds:
            continue
        segments.append(
            TranscriptSegment(
                start_seconds=start_seconds,
                end_seconds=end_seconds,
                text=text,
            )
        )

    return sorted(segments, key=lambda segment: segment.start_seconds)
