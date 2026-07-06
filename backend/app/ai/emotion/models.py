from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EmotionSegment:
    start_time: float
    end_time: float
    text: str
    emotion: str
    intensity: float
    reasons: list[str] = field(default_factory=list)
    source_segment_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "text": self.text,
            "emotion": self.emotion,
            "intensity": self.intensity,
            "reasons": self.reasons,
            "source_segment_id": self.source_segment_id,
        }


@dataclass
class EmotionDetectionResult:
    production_id: str
    segments: list[EmotionSegment]
    dominant_emotion: str
    average_intensity: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "segments": [segment.to_dict() for segment in self.segments],
            "dominant_emotion": self.dominant_emotion,
            "average_intensity": self.average_intensity,
            "metadata": self.metadata,
        }