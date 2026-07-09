from __future__ import annotations

from sqlalchemy.orm import Session

from app.asset.cache import AssetCacheLookupRequest, AssetCacheRuntime
from app.asset.download import AssetDownloadRequest, AssetDownloadRuntime
from app.asset.memory import build_production_asset_memory_runtime
from app.asset.ranking import AssetRankingRequest, AssetRankingRuntime
from app.asset.resolver.models import AssetResolveRequest, AssetResolveResult
from app.asset.runtime import AssetRuntime
from app.asset.search import AssetSearchRequest, AssetSearchRuntime


class AssetResolverRuntime:
    def __init__(
        self,
        db: Session,
        cache_runtime: AssetCacheRuntime | None = None,
        search_runtime: AssetSearchRuntime | None = None,
        ranking_runtime: AssetRankingRuntime | None = None,
        download_runtime: AssetDownloadRuntime | None = None,
        asset_runtime: AssetRuntime | None = None,
        asset_memory=None,
    ):
        self.db = db
        self.cache_runtime = cache_runtime or AssetCacheRuntime(db)
        self.search_runtime = search_runtime or AssetSearchRuntime()
        self.ranking_runtime = ranking_runtime or AssetRankingRuntime()
        self.download_runtime = download_runtime or AssetDownloadRuntime()
        self.asset_runtime = asset_runtime or AssetRuntime(db)
        self.asset_memory = asset_memory or build_production_asset_memory_runtime()

    def resolve(self, request: AssetResolveRequest) -> AssetResolveResult:
        production_id = request.metadata.get("production_id")

        cache_result = self.cache_runtime.lookup(
            AssetCacheLookupRequest(
                query=request.query,
                asset_type=request.asset_type,
                metadata=request.metadata,
            )
        )

        if cache_result.hit and cache_result.asset_id:
            provider_key = cache_result.payload.get("provider_key")
            provider_asset_id = cache_result.payload.get("provider_asset_id")

            if not self._already_used(
                production_id=production_id,
                provider_key=provider_key,
                provider_asset_id=provider_asset_id,
            ):
                return AssetResolveResult(
                    source="cache",
                    asset_id=str(cache_result.asset_id),
                    payload=cache_result.payload,
                    ranking_score=None,
                    metadata={
                        "cache_reason": cache_result.reason,
                        "query": request.query,
                        "asset_type": request.asset_type,
                        "memory_checked": bool(production_id),
                    },
                )

        search_result = self.search_runtime.search(
            AssetSearchRequest(
                query=request.query,
                asset_type=request.asset_type,
                provider_keys=request.provider_keys or [],
                per_page=request.per_page,
                orientation=request.preferred_orientation,
                metadata=request.metadata,
            )
        )

        ranking_result = self.ranking_runtime.rank(
            AssetRankingRequest(
                query=request.query,
                asset_type=request.asset_type,
                candidates=search_result.results,
                preferred_orientation=request.preferred_orientation,
                preferred_duration=request.preferred_duration,
                commercial_use=request.commercial_use,
                limit=10,
                metadata=request.metadata,
            )
        )

        if not ranking_result.ranked_assets:
            raise RuntimeError(
                f"No usable asset found for query={request.query}, asset_type={request.asset_type}"
            )

        selected = self._select_unused_ranked_asset(
            production_id=production_id,
            ranked_assets=ranking_result.ranked_assets,
        )

        downloaded = self.download_runtime.download(
            AssetDownloadRequest(
                asset=selected.asset,
                metadata={
                    "query": request.query,
                    "ranking_score": selected.score,
                },
            )
        )

        row = self.asset_runtime.save_provider_asset(
            asset=selected.asset,
            download_result=downloaded,
            status="ready",
        )

        return AssetResolveResult(
            source="download",
            asset_id=str(row.id),
            payload={
                "id": str(row.id),
                "provider_key": row.provider_key,
                "provider_asset_id": row.provider_asset_id,
                "asset_type": row.asset_type,
                "status": row.status,
                "title": row.title,
                "local_path": row.local_path,
                "checksum": row.checksum,
                "duration": row.duration,
                "width": row.width,
                "height": row.height,
                "license": row.license,
            },
            ranking_score=selected.score,
            metadata={
                "query": request.query,
                "asset_type": request.asset_type,
                "search": search_result.metadata,
                "ranking": ranking_result.metadata,
                "download": downloaded.metadata,
                "ranking_reasons": selected.reasons,
                "ranking_penalties": selected.penalties,
                "memory_checked": bool(production_id),
                "selected_provider_key": selected.asset.provider_key,
                "selected_provider_asset_id": selected.asset.provider_asset_id,
            },
        )

    def _select_unused_ranked_asset(
        self,
        production_id: str | None,
        ranked_assets,
    ):
        if not production_id:
            return ranked_assets[0]

        for item in ranked_assets:
            if not self._already_used(
                production_id=production_id,
                provider_key=item.asset.provider_key,
                provider_asset_id=item.asset.provider_asset_id,
            ):
                return item

        return ranked_assets[0]

    def _already_used(
        self,
        production_id: str | None,
        provider_key: str | None,
        provider_asset_id: str | None,
    ) -> bool:
        if not production_id:
            return False

        return self.asset_memory.has_used_provider_asset(
            production_id=production_id,
            provider_key=provider_key,
            provider_asset_id=provider_asset_id,
        )