from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AssetProviderSearchRequest:
    query: str
    asset_type: str
    page: int = 1
    per_page: int = 10
    orientation: str | None = None
    duration_min: float | None = None
    duration_max: float | None = None
    language: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AssetProviderSearchResult:
    provider_key: str
    provider_asset_id: str
    asset_type: str
    title: str | None = None
    description: str | None = None
    remote_url: str | None = None
    thumbnail_url: str | None = None
    preview_url: str | None = None
    duration: float | None = None
    width: int | None = None
    height: int | None = None
    license: str | None = None
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AssetProviderSearchResponse:
    provider_key: str
    query: str
    results: list[AssetProviderSearchResult]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AssetProviderHealthResult:
    provider_key: str
    enabled: bool
    configured: bool
    healthy: bool
    missing: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)