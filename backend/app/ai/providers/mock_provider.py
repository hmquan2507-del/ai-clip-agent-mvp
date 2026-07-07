from __future__ import annotations

from app.ai.providers.base import BaseAIProvider
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


class MockAIProvider(BaseAIProvider):
    provider_key = "mock"
    default_model = "mock-model"

    def generate(
        self,
        request: AIProviderRequest,
    ) -> AIProviderResponse:
        return AIProviderResponse(
            provider=self.provider_key,
            model=request.model or self.default_model,
            text="Mock provider response",
            raw={
                "prompt": request.prompt,
                "system_prompt": request.system_prompt,
            },
            metadata={
                "mode": "mock",
                "uses_real_api": False,
            },
        )

    def generate_json(
        self,
        request: AIProviderJSONRequest,
    ) -> AIProviderJSONResponse:
        return AIProviderJSONResponse(
            provider=self.provider_key,
            model=request.model or self.default_model,
            data={
                "mock": True,
                "prompt": request.prompt,
                "schema_keys": list(request.schema.keys()),
            },
            raw_text='{"mock": true}',
            raw={
                "schema": request.schema,
            },
            metadata={
                "mode": "mock",
                "uses_real_api": False,
            },
        )

    def embed(
        self,
        request: AIProviderEmbeddingRequest,
    ) -> AIProviderEmbeddingResponse:
        return AIProviderEmbeddingResponse(
            provider=self.provider_key,
            model=request.model or self.default_model,
            embedding=[0.0, 0.1, 0.2],
            metadata={
                "mode": "mock",
                "input_length": len(request.input_text),
                "uses_real_api": False,
            },
        )

    def vision(
        self,
        request: AIProviderVisionRequest,
    ) -> AIProviderVisionResponse:
        return AIProviderVisionResponse(
            provider=self.provider_key,
            model=request.model or self.default_model,
            text="Mock vision response",
            data={
                "image_count": len(request.image_paths),
                "video_frame_count": len(request.video_frame_paths),
            },
            raw={},
            metadata={
                "mode": "mock",
                "uses_real_api": False,
            },
        )

    def count_tokens(
        self,
        request: AIProviderTokenCountRequest,
    ) -> AIProviderTokenCountResponse:
        estimated_tokens = max(1, len(request.text.split()))

        return AIProviderTokenCountResponse(
            provider=self.provider_key,
            model=request.model or self.default_model,
            input_tokens=estimated_tokens,
            metadata={
                "mode": "mock",
                "strategy": "word_count_estimate",
                "uses_real_api": False,
            },
        )