from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CameraMovementPlan:
    segment_id: str
    target_id: str
    start_time: float
    end_time: float
    movement_type: str
    crop_mode: str = "center_crop"
    scale_from: float = 1.0
    scale_to: float = 1.08
    x_from: float = 0.5
    y_from: float = 0.5
    x_to: float = 0.5
    y_to: float = 0.5
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
            "movement_type": self.movement_type,
            "crop_mode": self.crop_mode,
            "scale_from": self.scale_from,
            "scale_to": self.scale_to,
            "x_from": self.x_from,
            "y_from": self.y_from,
            "x_to": self.x_to,
            "y_to": self.y_to,
            "metadata": self.metadata,
        }


@dataclass
class CameraMovementResult:
    production_id: str
    movements: list[CameraMovementPlan]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "movements": [item.to_dict() for item in self.movements],
            "metadata": self.metadata,
        }