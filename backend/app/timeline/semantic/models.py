from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TimelineSemanticSegment:
    segment_id: str
    start_time: float
    end_time: float
    text: str | None = None
    segment_type: str = "main_point"
    emotion: str = "neutral"
    importance_score: float = 0.5
    viral_potential_score: float = 0.5
    pacing: str = "normal"
    visual_density: str = "medium"
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        return max(0.0, self.end_time - self.start_time)


@dataclass
class TimelineSemanticAsset:
    asset_id: str
    asset_type: str
    track_type: str
    start_time: float
    end_time: float
    local_path: str | None = None
    provider_key: str | None = None
    title: str | None = None
    role: str = "supporting"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TimelineSemanticAnalysis:
    production_id: str
    segments: list[TimelineSemanticSegment]
    assets: list[TimelineSemanticAsset]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "segments": [segment.__dict__ for segment in self.segments],
            "assets": [asset.__dict__ for asset in self.assets],
            "metadata": self.metadata,
        }