from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.asset.providers.models import AssetProviderSearchResult


@dataclass
class AssetRankingRequest:
    query: str
    asset_type: str
    candidates: list[AssetProviderSearchResult]
    preferred_orientation: str | None = None
    preferred_duration: float | None = None
    commercial_use: bool = True
    limit: int = 10
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RankedAsset:
    asset: AssetProviderSearchResult
    score: float
    reasons: list[str] = field(default_factory=list)
    penalties: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AssetRankingResponse:
    query: str
    asset_type: str
    ranked_assets: list[RankedAsset]
    rejected_assets: list[RankedAsset] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)