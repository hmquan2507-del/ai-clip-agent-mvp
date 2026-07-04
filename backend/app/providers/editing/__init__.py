from app.providers.editing.base import BaseEditingProvider
from app.providers.editing.gemini import GeminiEditingProvider
from app.providers.editing.mock import MockEditingProvider


def get_editing_provider(provider: str | None = "gemini") -> BaseEditingProvider:
    if provider == "gemini":
        return GeminiEditingProvider()

    if provider == "mock":
        return MockEditingProvider()

    raise ValueError(f"Unsupported editing provider: {provider}")


__all__ = [
    "BaseEditingProvider",
    "GeminiEditingProvider",
    "MockEditingProvider",
    "get_editing_provider",
]