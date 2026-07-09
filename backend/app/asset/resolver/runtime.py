from __future__ import annotations

from sqlalchemy.orm import Session

from app.asset.cache import AssetCacheLookupRequest, AssetCacheRuntime
from app.asset.download import AssetDownloadRequest, AssetDownloadRuntime
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
    ):
        self.db = db
        self.cache_runtime = cache_runtime or AssetCacheRuntime(db)
        self.search_runtime = search_runtime or AssetSearchRuntime()
        self.ranking_runtime = ranking_runtime or AssetRankingRuntime()
        self.download_runtime = download_runtime or AssetDownloadRuntime()
        self.asset_runtime = asset_runtime or AssetRuntime(db)

    def resolve(self, request: AssetResolveRequest) -> AssetResolveResult:
        cache_result = self.cache_runtime.lookup(
            AssetCacheLookupRequest(
                query=request.query,
                asset_type=request.asset_type,
                metadata=request.metadata,
            )
        )

        if cache_result.hit and cache_result.asset_id:
            return AssetResolveResult(
                source="cache",
                asset_id=str(cache_result.asset_id),
                payload=cache_result.payload,
                ranking_score=None,
                metadata={
                    "cache_reason": cache_result.reason,
                    "query": request.query,
                    "asset_type": request.asset_type,
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
                limit=1,
                metadata=request.metadata,
            )
        )

        if not ranking_result.ranked_assets:
            raise RuntimeError(
                f"No usable asset found for query={request.query}, asset_type={request.asset_type}"
            )

        selected = ranking_result.ranked_assets[0]

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
            },
        )