from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TransitionPlan:
    segment_id: str
    target_id: str
    transition_type: str
    at_time: float
    duration: float = 0.25
    intensity: str = "medium"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "segment_id": self.segment_id,
            "target_id": self.target_id,
            "transition_type": self.transition_type,
            "at_time": self.at_time,
            "duration": self.duration,
            "intensity": self.intensity,
            "metadata": self.metadata,
        }


@dataclass
class TransitionPlanningResult:
    production_id: str
    transitions: list[TransitionPlan]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "transitions": [item.to_dict() for item in self.transitions],
            "metadata": self.metadata,
        }