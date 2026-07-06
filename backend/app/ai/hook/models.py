from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class HookCandidate:
    start_time: float
    end_time: float
    text: str
    score: float
    reasons: list[str] = field(default_factory=list)
    source_segment_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "text": self.text,
            "score": self.score,
            "reasons": self.reasons,
            "source_segment_id": self.source_segment_id,
        }


@dataclass
class HookDetectionResult:
    production_id: str
    hooks: list[HookCandidate]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "hooks": [hook.to_dict() for hook in self.hooks],
            "metadata": self.metadata,
        }