from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BrollPlacement:
    segment_id: str
    asset_id: str
    local_path: str | None
    start_time: float
    end_time: float
    placement_type: str
    layer: int = 2
    opacity: float = 1.0
    motion_hint: str | None = None
    transition_hint: str | None = None
    reason: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        return max(0.0, self.end_time - self.start_time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "segment_id": self.segment_id,
            "asset_id": self.asset_id,
            "local_path": self.local_path,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "placement_type": self.placement_type,
            "layer": self.layer,
            "opacity": self.opacity,
            "motion_hint": self.motion_hint,
            "transition_hint": self.transition_hint,
            "reason": self.reason,
            "metadata": self.metadata,
        }


@dataclass
class BrollPlacementResult:
    production_id: str
    placements: list[BrollPlacement]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "placements": [item.to_dict() for item in self.placements],
            "metadata": self.metadata,
        }