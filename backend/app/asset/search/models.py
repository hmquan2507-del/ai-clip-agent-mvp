from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.asset.providers.models import AssetProviderSearchResult


@dataclass
class AssetSearchRequest:
    query: str
    asset_type: str
    provider_keys: list[str] = field(default_factory=list)
    page: int = 1
    per_page: int = 10
    orientation: str | None = None
    duration_min: float | None = None
    duration_max: float | None = None
    language: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AssetSearchResponse:
    query: str
    asset_type: str
    results: list[AssetProviderSearchResult]
    provider_count: int
    metadata: dict[str, Any] = field(default_factory=dict)