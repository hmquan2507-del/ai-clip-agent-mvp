from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AssetResolveRequest:
    query: str
    asset_type: str
    preferred_duration: float | None = None
    preferred_orientation: str | None = None
    commercial_use: bool = True
    provider_keys: list[str] | None = None
    per_page: int = 5
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AssetResolveResult:
    source: str
    asset_id: str
    payload: dict[str, Any]
    ranking_score: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)