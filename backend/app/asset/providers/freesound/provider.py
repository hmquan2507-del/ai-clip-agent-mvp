from __future__ import annotations

from app.asset.providers.base import BaseAssetProvider
from app.asset.providers.freesound.client import FreesoundClient
from app.asset.providers.freesound.mapper import map_freesound_item
from app.asset.providers.models import (
    AssetProviderHealthResult,
    AssetProviderSearchRequest,
    AssetProviderSearchResponse,
)
from app.core.config import settings


class FreesoundProvider(BaseAssetProvider):
    provider_key = "freesound"

    def __init__(self, client: FreesoundClient | None = None):
        self.client = client or FreesoundClient()

    def search(self, request: AssetProviderSearchRequest) -> AssetProviderSearchResponse:
        data = self.client.text_search(
            query=request.query,
            page=request.page,
            page_size=request.per_page,
        )

        return AssetProviderSearchResponse(
            provider_key=self.provider_key,
            query=request.query,
            results=[map_freesound_item(item) for item in data.get("results", [])],
            metadata={
                "count": data.get("count"),
                "next": data.get("next"),
                "previous": data.get("previous"),
            },
        )

    def health(self) -> AssetProviderHealthResult:
        missing = []
        if not settings.freesound_api_key:
            missing.append("FREESOUND_API_KEY")

        configured = not missing

        return AssetProviderHealthResult(
            provider_key=self.provider_key,
            enabled=settings.enable_freesound,
            configured=configured,
            healthy=settings.enable_freesound and configured,
            missing=missing,
            metadata={"search_sound_supported": True},
        )