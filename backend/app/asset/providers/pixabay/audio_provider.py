from __future__ import annotations

from app.asset.providers.base import BaseAssetProvider
from app.asset.providers.models import (
    AssetProviderHealthResult,
    AssetProviderSearchRequest,
    AssetProviderSearchResponse,
)
from app.asset.providers.pixabay.audio_client import PixabayAudioClient
from app.asset.providers.pixabay.audio_mapper import map_pixabay_audio
from app.core.config import settings


class PixabayAudioProvider(BaseAssetProvider):
    provider_key = "pixabay_audio"

    def __init__(
        self,
        client: PixabayAudioClient | None = None,
    ):
        self.client = client or PixabayAudioClient()

    def search(
        self,
        request: AssetProviderSearchRequest,
    ) -> AssetProviderSearchResponse:
        data = self.client.search_audio(
            query=request.query,
            page=request.page,
            per_page=request.per_page,
        )

        results = [
            map_pixabay_audio(item=item, asset_type=request.asset_type)
            for item in data.get("hits", [])
        ]

        return AssetProviderSearchResponse(
            provider_key=self.provider_key,
            query=request.query,
            results=results,
            metadata={
                "total": data.get("total"),
                "total_hits": data.get("totalHits"),
                "audio_type": request.asset_type,
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
            metadata={
                "search_audio_supported": True,
            },
        )