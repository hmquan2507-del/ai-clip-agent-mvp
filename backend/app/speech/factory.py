from app.core.config import settings
from app.speech.base import SpeechProvider
from app.speech.gemini_provider import GeminiSpeechProvider
from app.speech.whisper_provider import WhisperSpeechProvider


def get_speech_provider() -> SpeechProvider:
    provider = getattr(settings, "speech_provider", "whisper").lower()

    if provider == "whisper":
        return WhisperSpeechProvider()

    if provider == "gemini":
        return GeminiSpeechProvider()

    raise ValueError(f"Unsupported speech provider: {provider}")