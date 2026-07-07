from __future__ import annotations

from app.ai.providers.models import (
    AIProviderEmbeddingRequest,
    AIProviderEmbeddingResponse,
    AIProviderJSONRequest,
    AIProviderJSONResponse,
    AIProviderRequest,
    AIProviderResponse,
    AIProviderTokenCountRequest,
    AIProviderTokenCountResponse,
    AIProviderVisionRequest,
    AIProviderVisionResponse,
)
from app.ai.providers.registry import AIProviderRegistry


class AIProviderManager:
    def __init__(self, registry: AIProviderRegistry):
        self.registry = registry

    def generate(
        self,
        provider_key: str,
        request: AIProviderRequest,
    ) -> AIProviderResponse:
        provider = self.registry.get(provider_key)
        return provider.generate(request)

    def generate_json(
        self,
        provider_key: str,
        request: AIProviderJSONRequest,
    ) -> AIProviderJSONResponse:
        provider = self.registry.get(provider_key)
        return provider.generate_json(request)

    def embed(
        self,
        provider_key: str,
        request: AIProviderEmbeddingRequest,
    ) -> AIProviderEmbeddingResponse:
        provider = self.registry.get(provider_key)
        return provider.embed(request)

    def vision(
        self,
        provider_key: str,
        request: AIProviderVisionRequest,
    ) -> AIProviderVisionResponse:
        provider = self.registry.get(provider_key)
        return provider.vision(request)

    def count_tokens(
        self,
        provider_key: str,
        request: AIProviderTokenCountRequest,
    ) -> AIProviderTokenCountResponse:
        provider = self.registry.get(provider_key)
        return provider.count_tokens(request)