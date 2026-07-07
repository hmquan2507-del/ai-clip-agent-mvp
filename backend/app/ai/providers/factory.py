from __future__ import annotations

from app.ai.providers.manager import AIProviderManager
from app.ai.providers.mock_provider import MockAIProvider
from app.ai.providers.registry import AIProviderRegistry
from app.core.config import settings


def build_default_provider_registry() -> AIProviderRegistry:
    registry = AIProviderRegistry()

    if settings.enable_gemini and settings.gemini_api_key:
        from app.ai.providers.gemini import GeminiProvider

        registry.register(GeminiProvider())

    if settings.enable_openai and settings.openai_api_key:
        from app.ai.providers.openai import OpenAIProvider

        registry.register(OpenAIProvider())

    registry.register(MockAIProvider())

    return registry


def build_default_provider_manager() -> AIProviderManager:
    return AIProviderManager(
        registry=build_default_provider_registry(),
    )