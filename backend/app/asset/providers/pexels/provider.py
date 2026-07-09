from __future__ import annotations

from app.asset.providers.base import BaseAssetProvider
from app.asset.providers.models import (
    AssetProviderHealthResult,
    AssetProviderSearchRequest,
    AssetProviderSearchResponse,
)
from app.asset.providers.pexels.client import PexelsClient
from app.asset.providers.pexels.mapper import map_pexels_video
from app.core.config import settings


class PexelsProvider(BaseAssetProvider):
    provider_key = "pexels"

    def __init__(self, client: PexelsClient | None = None):
        self.client = client or PexelsClient()

    def search(self, request: AssetProviderSearchRequest) -> AssetProviderSearchResponse:
        attempts: list[dict] = []

        search_attempts = [
            {
                "query": request.query,
                "orientation": request.orientation,
                "reason": "original",
            },
            {
                "query": request.query,
                "orientation": None,
                "reason": "without_orientation",
            },
            {
                "query": self._fallback_query(request.query),
                "orientation": None,
                "reason": "fallback_query",
            },
        ]

        last_error: str | None = None

        for attempt in search_attempts:
            try:
                data = self.client.search_videos(
                    query=attempt["query"],
                    page=request.page,
                    per_page=request.per_page,
                    orientation=attempt["orientation"],
                )

                return AssetProviderSearchResponse(
                    provider_key=self.provider_key,
                    query=request.query,
                    results=[map_pexels_video(item) for item in data.get("videos", [])],
                    metadata={
                        "status": "ok",
                        "attempt_reason": attempt["reason"],
                        "actual_query": attempt["query"],
                        "orientation": attempt["orientation"],
                        "page": data.get("page"),
                        "per_page": data.get("per_page"),
                        "total_results": data.get("total_results"),
                        "attempts": attempts,
                    },
                )

            except Exception as error:
                last_error = str(error)
                attempts.append(
                    {
                        "reason": attempt["reason"],
                        "query": attempt["query"],
                        "orientation": attempt["orientation"],
                        "error": last_error,
                    }
                )

        return AssetProviderSearchResponse(
            provider_key=self.provider_key,
            query=request.query,
            results=[],
            metadata={
                "status": "failed",
                "error": last_error,
                "attempts": attempts,
            },
        )

    def health(self) -> AssetProviderHealthResult:
        missing = []

        if not settings.pexels_api_key:
            missing.append("PEXELS_API_KEY")

        configured = not missing

        return AssetProviderHealthResult(
            provider_key=self.provider_key,
            enabled=settings.enable_pexels,
            configured=configured,
            healthy=settings.enable_pexels and configured,
            missing=missing,
            metadata={"search_video_supported": True},
        )

    def _fallback_query(self, query: str) -> str:
        cleaned = query.strip()

        if not cleaned:
            return "business"

        words = cleaned.split()

        if len(words) <= 2:
            return cleaned

        return " ".join(words[:2])