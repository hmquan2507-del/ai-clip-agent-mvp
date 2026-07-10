from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SubtitleTimingSegment:
    segment_id: str
    start_time: float
    end_time: float
    text: str
    segment_type: str = "main_point"
    importance_score: float = 0.5
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        return max(0.0, self.end_time - self.start_time)


@dataclass
class OptimizedSubtitleCue:
    cue_id: str
    segment_id: str
    start_time: float
    end_time: float
    text: str
    word_count: int
    characters_per_second: float
    importance_score: float = 0.5
    highlight_words: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        return max(0.0, self.end_time - self.start_time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "cue_id": self.cue_id,
            "segment_id": self.segment_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "text": self.text,
            "word_count": self.word_count,
            "characters_per_second": self.characters_per_second,
            "importance_score": self.importance_score,
            "highlight_words": self.highlight_words,
            "metadata": self.metadata,
        }


@dataclass
class SubtitleTimingResult:
    production_id: str
    cues: list[OptimizedSubtitleCue]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "cues": [cue.to_dict() for cue in self.cues],
            "metadata": self.metadata,
        }