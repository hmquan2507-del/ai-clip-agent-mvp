from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AssetReference:
    asset_id: str
    track_type: str
    start_time: float
    end_time: float

    layer: int = 0
    volume: float | None = None
    opacity: float | None = None
    speed: float | None = None
    transform: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        return max(0.0, self.end_time - self.start_time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "track_type": self.track_type,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "layer": self.layer,
            "volume": self.volume,
            "opacity": self.opacity,
            "speed": self.speed,
            "transform": self.transform,
            "metadata": self.metadata,
        }