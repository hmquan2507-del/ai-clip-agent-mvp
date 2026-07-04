from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class TranscriptSegmentResult:
    start_time: float
    end_time: float
    text: str
    speaker: str | None = None
    confidence: float | None = None


@dataclass
class TranscriptResult:
    language: str | None
    duration: float | None
    provider: str
    text: str
    segments: list[TranscriptSegmentResult]


class SpeechProvider(ABC):
    @abstractmethod
    def transcribe(self, file_path: str) -> TranscriptResult:
        raise NotImplementedError