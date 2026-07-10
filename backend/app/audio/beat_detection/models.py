from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BeatDetectionRequest:
    audio_path: str
    start_time: float = 0.0
    end_time: float | None = None
    expected_bpm: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class BeatPoint:
    beat_index: int
    time: float
    strength: float = 1.0
    is_downbeat: bool = False
    bar_index: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "beat_index": self.beat_index,
            "time": self.time,
            "strength": self.strength,
            "is_downbeat": self.is_downbeat,
            "bar_index": self.bar_index,
            "metadata": self.metadata,
        }


@dataclass
class BeatSection:
    section_id: str
    start_time: float
    end_time: float
    section_type: str
    energy: float
    beat_indices: list[int] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        return max(0.0, self.end_time - self.start_time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "section_id": self.section_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "section_type": self.section_type,
            "energy": self.energy,
            "beat_indices": self.beat_indices,
            "metadata": self.metadata,
        }


@dataclass
class BeatDetectionResult:
    audio_path: str
    bpm: float
    confidence: float
    beats: list[BeatPoint]
    sections: list[BeatSection]
    duration: float
    provider_key: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "audio_path": self.audio_path,
            "bpm": self.bpm,
            "confidence": self.confidence,
            "duration": self.duration,
            "provider_key": self.provider_key,
            "beats": [beat.to_dict() for beat in self.beats],
            "sections": [section.to_dict() for section in self.sections],
            "metadata": self.metadata,
        }