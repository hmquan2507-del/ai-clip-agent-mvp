from __future__ import annotations

from abc import ABC, abstractmethod

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


class BaseAIProvider(ABC):
    provider_key: str = "base"
    default_model: str = "none"

    @abstractmethod
    def generate(
        self,
        request: AIProviderRequest,
    ) -> AIProviderResponse:
        raise NotImplementedError

    @abstractmethod
    def generate_json(
        self,
        request: AIProviderJSONRequest,
    ) -> AIProviderJSONResponse:
        raise NotImplementedError

    @abstractmethod
    def embed(
        self,
        request: AIProviderEmbeddingRequest,
    ) -> AIProviderEmbeddingResponse:
        raise NotImplementedError

    @abstractmethod
    def vision(
        self,
        request: AIProviderVisionRequest,
    ) -> AIProviderVisionResponse:
        raise NotImplementedError

    @abstractmethod
    def count_tokens(
        self,
        request: AIProviderTokenCountRequest,
    ) -> AIProviderTokenCountResponse:
        raise NotImplementedError