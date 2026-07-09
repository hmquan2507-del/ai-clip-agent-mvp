from __future__ import annotations

from app.asset.providers import (
    AssetProviderSearchRequest,
    build_default_asset_provider_runtime,
)
from app.asset.providers.runtime import AssetProviderRuntime
from app.asset.search.models import AssetSearchRequest, AssetSearchResponse


class AssetSearchRuntime:
    def __init__(
        self,
        provider_runtime: AssetProviderRuntime | None = None,
    ):
        self.provider_runtime = provider_runtime or build_default_asset_provider_runtime()

    def search(
        self,
        request: AssetSearchRequest,
    ) -> AssetSearchResponse:
        provider_keys = request.provider_keys or self._default_providers_for_type(
            request.asset_type
        )

        provider_request = AssetProviderSearchRequest(
            query=request.query,
            asset_type=request.asset_type,
            page=request.page,
            per_page=request.per_page,
            orientation=request.orientation,
            duration_min=request.duration_min,
            duration_max=request.duration_max,
            language=request.language,
            metadata=request.metadata,
        )

        provider_responses = self.provider_runtime.search_many(
            provider_keys=provider_keys,
            request=provider_request,
        )

        results = []

        provider_metadata = []

        for response in provider_responses:
            results.extend(response.results)
            provider_metadata.append(
                {
                    "provider_key": response.provider_key,
                    "result_count": len(response.results),
                    "metadata": response.metadata,
                }
            )

        return AssetSearchResponse(
            query=request.query,
            asset_type=request.asset_type,
            results=results,
            provider_count=len(provider_keys),
            metadata={
                "providers": provider_metadata,
                "total_results": len(results),
            },
        )

    def _default_providers_for_type(
        self,
        asset_type: str,
    ) -> list[str]:
        normalized = asset_type.lower()

        if normalized in {"broll", "video", "image"}:
            return ["pexels", "pixabay"]

        if normalized in {"sound_effect", "sfx"}:
            return ["freesound", "pixabay"]

        if normalized in {"music"}:
            return ["pixabay"]

        return ["pexels", "pixabay", "freesound"]