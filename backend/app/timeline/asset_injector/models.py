from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TimelineAssetInstruction:
    query: str
    asset_type: str
    track_type: str
    start_time: float
    end_time: float

    preferred_orientation: str | None = None
    preferred_duration: float | None = None
    layer: int = 1
    volume: float | None = None
    opacity: float | None = None
    speed: float | None = None
    commercial_use: bool = True
    provider_keys: list[str] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        return max(0.0, self.end_time - self.start_time)


@dataclass
class TimelineAssetClip:
    asset_id: str
    asset_type: str
    track_type: str
    start_time: float
    end_time: float
    layer: int
    local_path: str | None = None
    title: str | None = None
    volume: float | None = None
    opacity: float | None = None
    speed: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        return max(0.0, self.end_time - self.start_time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "asset_type": self.asset_type,
            "track_type": self.track_type,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "layer": self.layer,
            "local_path": self.local_path,
            "title": self.title,
            "volume": self.volume,
            "opacity": self.opacity,
            "speed": self.speed,
            "metadata": self.metadata,
        }


@dataclass
class TimelineAssetInjectionRequest:
    production_id: str
    instructions: list[TimelineAssetInstruction]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TimelineAssetInjectionResult:
    production_id: str
    asset_clips: list[TimelineAssetClip]
    failed_instructions: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "asset_clips": [clip.to_dict() for clip in self.asset_clips],
            "failed_instructions": self.failed_instructions,
            "metadata": self.metadata,
        }