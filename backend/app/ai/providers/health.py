from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.core.config import settings


@dataclass
class AIProviderHealth:
    provider_key: str
    enabled: bool
    configured: bool
    default_model: str
    missing: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_key": self.provider_key,
            "enabled": self.enabled,
            "configured": self.configured,
            "default_model": self.default_model,
            "missing": self.missing,
            "metadata": self.metadata,
        }


class AIProviderHealthChecker:
    def check_all(self) -> dict[str, Any]:
        providers = [
            self.check_gemini(),
            self.check_openai(),
            self.check_claude(),
            self.check_mock(),
        ]

        return {
            "default_ai_provider": settings.default_ai_provider,
            "providers": [provider.to_dict() for provider in providers],
            "metadata": {
                "service": "ai_provider_health_checker",
                "configured_count": sum(1 for item in providers if item.configured),
                "enabled_count": sum(1 for item in providers if item.enabled),
            },
        }

    def check_gemini(self) -> AIProviderHealth:
        missing: list[str] = []

        if not settings.gemini_api_key:
            missing.append("GEMINI_API_KEY")

        if not settings.gemini_model:
            missing.append("GEMINI_MODEL")

        return AIProviderHealth(
            provider_key="gemini",
            enabled=settings.enable_gemini,
            configured=len(missing) == 0,
            default_model=settings.gemini_model,
            missing=missing,
            metadata={
                "api_key_loaded": bool(settings.gemini_api_key),
                "uses_real_api": True,
            },
        )

    def check_openai(self) -> AIProviderHealth:
        missing: list[str] = []

        if not settings.openai_api_key:
            missing.append("OPENAI_API_KEY")

        if not settings.openai_model:
            missing.append("OPENAI_MODEL")

        return AIProviderHealth(
            provider_key="openai",
            enabled=settings.enable_openai,
            configured=len(missing) == 0,
            default_model=settings.openai_model,
            missing=missing,
            metadata={
                "api_key_loaded": bool(settings.openai_api_key),
                "uses_real_api": True,
            },
        )

    def check_claude(self) -> AIProviderHealth:
        missing: list[str] = []

        if not settings.claude_api_key:
            missing.append("CLAUDE_API_KEY")

        if not settings.claude_model:
            missing.append("CLAUDE_MODEL")

        return AIProviderHealth(
            provider_key="claude",
            enabled=settings.enable_claude,
            configured=len(missing) == 0,
            default_model=settings.claude_model,
            missing=missing,
            metadata={
                "api_key_loaded": bool(settings.claude_api_key),
                "uses_real_api": True,
            },
        )

    def check_mock(self) -> AIProviderHealth:
        return AIProviderHealth(
            provider_key="mock",
            enabled=True,
            configured=True,
            default_model="mock-model",
            missing=[],
            metadata={
                "uses_real_api": False,
            },
        )