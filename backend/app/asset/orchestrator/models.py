from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.timeline.asset_injector.models import TimelineAssetClip


@dataclass
class AssetPlanItem:
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


@dataclass
class AssetOrchestrationRequest:
    production_id: str
    plan_items: list[AssetPlanItem]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AssetOrchestrationResult:
    production_id: str
    asset_clips: list[TimelineAssetClip]
    failed_items: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "asset_clips": [clip.to_dict() for clip in self.asset_clips],
            "failed_items": self.failed_items,
            "metadata": self.metadata,
        }