from __future__ import annotations

from app.ai.providers.base import BaseAIProvider


class AIProviderRegistry:
    def __init__(self):
        self._providers: dict[str, BaseAIProvider] = {}

    def register(self, provider: BaseAIProvider) -> None:
        if not provider.provider_key:
            raise ValueError("Provider key is required")

        self._providers[provider.provider_key] = provider

    def get(self, provider_key: str) -> BaseAIProvider:
        provider = self._providers.get(provider_key)

        if provider is None:
            raise ValueError(f"AI provider not registered: {provider_key}")

        return provider

    def has(self, provider_key: str) -> bool:
        return provider_key in self._providers

    def keys(self) -> list[str]:
        return sorted(self._providers.keys())

    def describe(self) -> list[dict]:
        return [
            {
                "provider_key": provider.provider_key,
                "default_model": provider.default_model,
                "class_name": provider.__class__.__name__,
            }
            for provider in self._providers.values()
        ]