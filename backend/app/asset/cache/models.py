from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AssetCacheLookupRequest:
    query: str
    asset_type: str
    provider_key: str | None = None
    provider_asset_id: str | None = None
    checksum: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AssetCacheLookupResult:
    hit: bool
    asset_id: str | None = None
    reason: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)