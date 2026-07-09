from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ShotSelection:
    segment_id: str
    start_time: float
    end_time: float
    shot_type: str
    priority: str
    reason: str
    asset_role: str | None = None
    motion_hint: str | None = None
    transition_hint: str | None = None
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
            "shot_type": self.shot_type,
            "priority": self.priority,
            "reason": self.reason,
            "asset_role": self.asset_role,
            "motion_hint": self.motion_hint,
            "transition_hint": self.transition_hint,
            "metadata": self.metadata,
        }


@dataclass
class ShotSelectionResult:
    production_id: str
    shots: list[ShotSelection]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "shots": [shot.to_dict() for shot in self.shots],
            "metadata": self.metadata,
        }