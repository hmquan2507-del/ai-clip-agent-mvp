from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.asset.providers.models import AssetProviderSearchResult


@dataclass
class AssetDownloadRequest:
    asset: AssetProviderSearchResult
    storage_root: str = "storage/assets"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AssetDownloadResult:
    provider_key: str
    provider_asset_id: str
    asset_type: str
    local_path: str
    checksum: str
    file_size: int
    content_type: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)