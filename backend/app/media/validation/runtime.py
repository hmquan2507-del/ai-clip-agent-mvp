from __future__ import annotations

import json
import subprocess
from pathlib import Path

from app.media.validation.models import MediaValidationResult


class MediaValidationRuntime:
    def __init__(
        self,
        ffprobe_binary: str = "ffprobe",
        timeout_seconds: int = 30,
    ):
        self.ffprobe_binary = ffprobe_binary
        self.timeout_seconds = timeout_seconds

    def validate(
        self,
        local_path: str,
        require_video: bool = True,
    ) -> MediaValidationResult:
        path = Path(local_path)
        errors: list[str] = []

        if not path.exists():
            return MediaValidationResult(
                local_path=local_path,
                valid=False,
                errors=["file_not_found"],
            )

        if not path.is_file():
            return MediaValidationResult(
                local_path=local_path,
                valid=False,
                errors=["path_is_not_file"],
            )

        if path.stat().st_size <= 0:
            return MediaValidationResult(
                local_path=local_path,
                valid=False,
                errors=["empty_file"],
            )

        command = [
            self.ffprobe_binary,
            "-v",
            "error",
            "-show_streams",
            "-show_format",
            "-of",
            "json",
            str(path),
        ]

        try:
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
        except FileNotFoundError:
            return MediaValidationResult(
                local_path=local_path,
                valid=False,
                errors=["ffprobe_not_installed"],
            )
        except subprocess.TimeoutExpired:
            return MediaValidationResult(
                local_path=local_path,
                valid=False,
                errors=["ffprobe_timeout"],
            )

        if completed.returncode != 0:
            return MediaValidationResult(
                local_path=local_path,
                valid=False,
                errors=[
                    "ffprobe_failed",
                    completed.stderr.strip() or "unknown_ffprobe_error",
                ],
            )

        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError:
            return MediaValidationResult(
                local_path=local_path,
                valid=False,
                errors=["invalid_ffprobe_json"],
            )

        streams = payload.get("streams") or []
        format_payload = payload.get("format") or {}

        video_stream = next(
            (
                item
                for item in streams
                if item.get("codec_type") == "video"
            ),
            None,
        )

        audio_stream = next(
            (
                item
                for item in streams
                if item.get("codec_type") == "audio"
            ),
            None,
        )

        duration = self._float_or_none(
            format_payload.get("duration")
        )

        if duration is None or duration <= 0:
            errors.append("invalid_duration")

        if require_video and video_stream is None:
            errors.append("missing_video_stream")

        fps = self._parse_fps(
            video_stream.get("avg_frame_rate")
            if video_stream
            else None
        )

        return MediaValidationResult(
            local_path=str(path),
            valid=not errors,
            duration=duration,
            width=(
                int(video_stream["width"])
                if video_stream and video_stream.get("width")
                else None
            ),
            height=(
                int(video_stream["height"])
                if video_stream and video_stream.get("height")
                else None
            ),
            fps=fps,
            video_codec=(
                video_stream.get("codec_name")
                if video_stream
                else None
            ),
            audio_codec=(
                audio_stream.get("codec_name")
                if audio_stream
                else None
            ),
            has_video=video_stream is not None,
            has_audio=audio_stream is not None,
            errors=errors,
            metadata={
                "file_size": path.stat().st_size,
                "format_name": format_payload.get("format_name"),
            },
        )

    def _float_or_none(
        self,
        value,
    ) -> float | None:
        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _parse_fps(
        self,
        value: str | None,
    ) -> float | None:
        if not value:
            return None

        if "/" not in value:
            return self._float_or_none(value)

        numerator, denominator = value.split("/", 1)

        try:
            denominator_value = float(denominator)

            if denominator_value == 0:
                return None

            return round(
                float(numerator) / denominator_value,
                3,
            )
        except (TypeError, ValueError):
            return None