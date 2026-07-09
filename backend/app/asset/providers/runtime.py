from __future__ import annotations

from app.asset.providers.models import (
    AssetProviderHealthResult,
    AssetProviderSearchRequest,
    AssetProviderSearchResponse,
)
from app.asset.providers.registry import AssetProviderRegistry


class AssetProviderRuntime:
    def __init__(self, registry: AssetProviderRegistry):
        self.registry = registry

    def search(
        self,
        provider_key: str,
        request: AssetProviderSearchRequest,
    ) -> AssetProviderSearchResponse:
        provider = self.registry.resolve(provider_key)
        return provider.search(request)

    def search_many(
        self,
        provider_keys: list[str],
        request: AssetProviderSearchRequest,
    ) -> list[AssetProviderSearchResponse]:
        responses: list[AssetProviderSearchResponse] = []

        for provider_key in provider_keys:
            try:
                responses.append(self.search(provider_key, request))
            except Exception as error:
                responses.append(
                    AssetProviderSearchResponse(
                        provider_key=provider_key,
                        query=request.query,
                        results=[],
                        metadata={
                            "status": "failed",
                            "error": str(error),
                        },
                    )
                )

        return responses

    def health_all(self) -> list[AssetProviderHealthResult]:
        return [provider.health() for provider in self.registry.list()]