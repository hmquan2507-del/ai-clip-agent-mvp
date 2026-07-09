from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProductionAssetUsage:
    production_id: str
    asset_id: str | None
    provider_key: str | None
    provider_asset_id: str | None
    asset_type: str
    track_type: str | None
    start_time: float
    end_time: float
    query: str | None = None
    local_path: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AssetMemoryRecordRequest:
    production_id: str
    usages: list[ProductionAssetUsage]


@dataclass
class AssetMemoryLookupRequest:
    production_id: str
    asset_type: str | None = None


@dataclass
class AssetMemoryLookupResult:
    production_id: str
    usages: list[ProductionAssetUsage]

    def used_provider_asset_ids(self) -> set[tuple[str, str]]:
        return {
            (item.provider_key, item.provider_asset_id)
            for item in self.usages
            if item.provider_key and item.provider_asset_id
        }

    def used_local_paths(self) -> set[str]:
        return {
            item.local_path
            for item in self.usages
            if item.local_path
        }