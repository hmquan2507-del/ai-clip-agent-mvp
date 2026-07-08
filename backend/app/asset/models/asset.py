from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.asset.enums import AssetStatus, AssetType, ProviderKey


@dataclass
class AssetDomain:
    provider_key: ProviderKey | str
    asset_type: AssetType | str
    status: AssetStatus | str = AssetStatus.DISCOVERED

    provider_asset_id: str | None = None
    title: str | None = None
    description: str | None = None

    tags: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    local_path: str | None = None
    remote_url: str | None = None
    thumbnail_url: str | None = None
    preview_url: str | None = None

    checksum: str | None = None
    duration: float | None = None
    width: int | None = None
    height: int | None = None
    fps: float | None = None
    file_size: int | None = None

    license: str | None = None
    language: str | None = None