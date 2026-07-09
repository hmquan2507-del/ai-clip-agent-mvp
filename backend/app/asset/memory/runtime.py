from __future__ import annotations

from app.asset.memory.models import (
    AssetMemoryLookupRequest,
    AssetMemoryLookupResult,
    AssetMemoryRecordRequest,
    ProductionAssetUsage,
)


class ProductionAssetMemoryRuntime:
    def __init__(self):
        self._usages: dict[str, list[ProductionAssetUsage]] = {}

    def record(
        self,
        request: AssetMemoryRecordRequest,
    ) -> None:
        existing = self._usages.setdefault(request.production_id, [])

        for usage in request.usages:
            key = (
                usage.provider_key,
                usage.provider_asset_id,
                usage.asset_type,
                usage.start_time,
                usage.end_time,
            )

            duplicate = any(
                (
                    item.provider_key,
                    item.provider_asset_id,
                    item.asset_type,
                    item.start_time,
                    item.end_time,
                )
                == key
                for item in existing
            )

            if not duplicate:
                existing.append(usage)

    def lookup(
        self,
        request: AssetMemoryLookupRequest,
    ) -> AssetMemoryLookupResult:
        usages = self._usages.get(request.production_id, [])

        if request.asset_type:
            usages = [
                item for item in usages
                if item.asset_type == request.asset_type
            ]

        return AssetMemoryLookupResult(
            production_id=request.production_id,
            usages=list(usages),
        )

    def has_used_provider_asset(
        self,
        production_id: str,
        provider_key: str | None,
        provider_asset_id: str | None,
    ) -> bool:
        if not provider_key or not provider_asset_id:
            return False

        result = self.lookup(
            AssetMemoryLookupRequest(
                production_id=production_id,
            )
        )

        return (provider_key, provider_asset_id) in result.used_provider_asset_ids()