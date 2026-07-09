from __future__ import annotations

from app.asset.providers.base import BaseAssetProvider
from app.asset.providers.models import (
    AssetProviderHealthResult,
    AssetProviderSearchRequest,
    AssetProviderSearchResponse,
)
from app.asset.providers.pixabay.client import PixabayClient
from app.asset.providers.pixabay.mapper import map_pixabay_video
from app.core.config import settings


class PixabayProvider(BaseAssetProvider):
    provider_key = "pixabay"

    def __init__(self, client: PixabayClient | None = None):
        self.client = client or PixabayClient()

    def search(self, request: AssetProviderSearchRequest) -> AssetProviderSearchResponse:
        data = self.client.search_videos(
            query=request.query,
            page=request.page,
            per_page=request.per_page,
        )

        return AssetProviderSearchResponse(
            provider_key=self.provider_key,
            query=request.query,
            results=[map_pixabay_video(item) for item in data.get("hits", [])],
            metadata={
                "total": data.get("total"),
                "total_hits": data.get("totalHits"),
            },
        )

    def health(self) -> AssetProviderHealthResult:
        missing = []
        if not settings.pixabay_api_key:
            missing.append("PIXABAY_API_KEY")

        configured = not missing

        return AssetProviderHealthResult(
            provider_key=self.provider_key,
            enabled=settings.enable_pixabay,
            configured=configured,
            healthy=settings.enable_pixabay and configured,
            missing=missing,
            metadata={"search_video_supported": True},
        )