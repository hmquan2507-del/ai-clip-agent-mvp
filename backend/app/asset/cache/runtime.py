from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.asset.cache.models import AssetCacheLookupRequest, AssetCacheLookupResult
from app.repositories.asset_repository import AssetRepository


class AssetCacheRuntime:
    def __init__(self, db: Session):
        self.repository = AssetRepository(db)

    def lookup(
        self,
        request: AssetCacheLookupRequest,
    ) -> AssetCacheLookupResult:
        if request.checksum:
            asset = self.repository.find_by_checksum(request.checksum)

            if asset is not None:
                return self._hit(asset, "checksum_match")

        if request.provider_key and request.provider_asset_id:
            asset = self.repository.find_ready_by_provider_asset(
                provider_key=request.provider_key,
                provider_asset_id=request.provider_asset_id,
            )

            if asset is not None:
                return self._hit(asset, "provider_asset_match")

        semantic_asset = self._simple_keyword_lookup(
            query=request.query,
            asset_type=request.asset_type,
        )

        if semantic_asset is not None:
            return self._hit(semantic_asset, "keyword_cache_match")

        return AssetCacheLookupResult(
            hit=False,
            reason="cache_miss",
        )

    def _simple_keyword_lookup(
        self,
        query: str,
        asset_type: str,
    ):
        query_tokens = self._tokens(query)

        if not query_tokens:
            return None

        candidates = self.repository.find_ready_by_type(asset_type=asset_type, limit=100)

        best_asset = None
        best_score = 0

        for asset in candidates:
            corpus = " ".join(
                [
                    asset.title or "",
                    asset.description or "",
                    " ".join(self._safe_json_list(asset.tags_json)),
                    " ".join(self._safe_json_list(asset.keywords_json)),
                ]
            )

            corpus_tokens = self._tokens(corpus)
            overlap = query_tokens.intersection(corpus_tokens)
            score = len(overlap)

            if score > best_score:
                best_score = score
                best_asset = asset

        if best_asset is None or best_score <= 0:
            return None

        return best_asset

    def _hit(self, asset, reason: str) -> AssetCacheLookupResult:
        return AssetCacheLookupResult(
            hit=True,
            asset_id=asset.id,
            reason=reason,
            payload={
                "id": asset.id,
                "provider_key": asset.provider_key,
                "provider_asset_id": asset.provider_asset_id,
                "asset_type": asset.asset_type,
                "status": asset.status,
                "title": asset.title,
                "local_path": asset.local_path,
                "checksum": asset.checksum,
                "duration": asset.duration,
                "width": asset.width,
                "height": asset.height,
                "license": asset.license,
            },
        )

    def _tokens(self, text: str) -> set[str]:
        normalized = (
            text.lower()
            .replace(",", " ")
            .replace(".", " ")
            .replace("-", " ")
            .replace("_", " ")
            .replace("/", " ")
        )
        return {item.strip() for item in normalized.split() if len(item.strip()) >= 3}

    def _safe_json_list(self, value: str | None) -> list[str]:
        if not value:
            return []

        try:
            data = json.loads(value)
        except json.JSONDecodeError:
            return []

        if not isinstance(data, list):
            return []

        return [str(item) for item in data]