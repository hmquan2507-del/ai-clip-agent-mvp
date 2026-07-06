from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class StoryBeat:
    beat_type: str
    start_time: float
    end_time: float
    text: str
    score: float
    reasons: list[str] = field(default_factory=list)
    source_segment_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "beat_type": self.beat_type,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "text": self.text,
            "score": self.score,
            "reasons": self.reasons,
            "source_segment_id": self.source_segment_id,
        }


@dataclass
class StoryArc:
    arc_type: str
    beats: list[StoryBeat]
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "arc_type": self.arc_type,
            "beats": [beat.to_dict() for beat in self.beats],
            "score": self.score,
            "metadata": self.metadata,
        }


@dataclass
class StoryDetectionResult:
    production_id: str
    arcs: list[StoryArc]
    beats: list[StoryBeat]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "arcs": [arc.to_dict() for arc in self.arcs],
            "beats": [beat.to_dict() for beat in self.beats],
            "metadata": self.metadata,
        }