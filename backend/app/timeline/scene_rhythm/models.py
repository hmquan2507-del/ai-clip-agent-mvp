from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SceneRhythmEvent:
    event_id: str
    segment_id: str
    event_type: str
    original_time: float
    aligned_time: float
    alignment_delta: float
    beat_index: int | None = None
    beat_strength: float | None = None
    is_downbeat: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "segment_id": self.segment_id,
            "event_type": self.event_type,
            "original_time": self.original_time,
            "aligned_time": self.aligned_time,
            "alignment_delta": self.alignment_delta,
            "beat_index": self.beat_index,
            "beat_strength": self.beat_strength,
            "is_downbeat": self.is_downbeat,
            "metadata": self.metadata,
        }


@dataclass
class SceneRhythmSegment:
    segment_id: str
    start_time: float
    end_time: float
    rhythm_type: str
    pacing: str
    energy: float
    beat_alignment_score: float
    subtitle_alignment_score: float
    motion_alignment_score: float
    transition_alignment_score: float
    overall_score: float
    events: list[SceneRhythmEvent] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        return max(0.0, self.end_time - self.start_time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "segment_id": self.segment_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "rhythm_type": self.rhythm_type,
            "pacing": self.pacing,
            "energy": self.energy,
            "beat_alignment_score": self.beat_alignment_score,
            "subtitle_alignment_score": self.subtitle_alignment_score,
            "motion_alignment_score": self.motion_alignment_score,
            "transition_alignment_score": self.transition_alignment_score,
            "overall_score": self.overall_score,
            "events": [event.to_dict() for event in self.events],
            "metadata": self.metadata,
        }


@dataclass
class SceneRhythmResult:
    production_id: str
    segments: list[SceneRhythmSegment]
    events: list[SceneRhythmEvent]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "segments": [segment.to_dict() for segment in self.segments],
            "events": [event.to_dict() for event in self.events],
            "metadata": self.metadata,
        }