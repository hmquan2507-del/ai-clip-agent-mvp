from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MotionPlan:
    segment_id: str
    target_id: str
    start_time: float
    end_time: float
    motion_type: str
    intensity: str = "medium"
    easing: str = "ease_out"
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        return max(0.0, self.end_time - self.start_time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "segment_id": self.segment_id,
            "target_id": self.target_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "motion_type": self.motion_type,
            "intensity": self.intensity,
            "easing": self.easing,
            "metadata": self.metadata,
        }


@dataclass
class MotionPlanningResult:
    production_id: str
    motions: list[MotionPlan]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "motions": [item.to_dict() for item in self.motions],
            "metadata": self.metadata,
        }