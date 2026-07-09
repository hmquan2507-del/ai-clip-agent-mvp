from __future__ import annotations

from app.asset.providers.base import BaseAssetProvider


class AssetProviderRegistry:
    def __init__(self):
        self._providers: dict[str, BaseAssetProvider] = {}

    def register(self, provider: BaseAssetProvider) -> None:
        if provider.provider_key in self._providers:
            raise ValueError(f"Asset provider already registered: {provider.provider_key}")

        self._providers[provider.provider_key] = provider

    def resolve(self, provider_key: str) -> BaseAssetProvider:
        provider = self._providers.get(provider_key)

        if provider is None:
            raise ValueError(f"Asset provider not registered: {provider_key}")

        return provider

    def list(self) -> list[BaseAssetProvider]:
        return list(self._providers.values())

    def exists(self, provider_key: str) -> bool:
        return provider_key in self._providers