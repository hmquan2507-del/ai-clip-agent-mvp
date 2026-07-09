from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.asset.providers.models import AssetProviderSearchResult


@dataclass
class AudioSearchRequest:
    query: str
    audio_type: str  # music | sound_effect
    page: int = 1
    per_page: int = 10
    commercial_use: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AudioSearchResponse:
    provider_key: str
    query: str
    audio_type: str
    results: list[AssetProviderSearchResult]
    metadata: dict[str, Any] = field(default_factory=dict)