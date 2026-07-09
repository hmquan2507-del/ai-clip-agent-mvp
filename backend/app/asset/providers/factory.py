from __future__ import annotations

from app.asset.providers.pexels import PexelsProvider
from app.asset.providers.pixabay import PixabayProvider
from app.asset.providers.freesound import FreesoundProvider
from app.asset.providers.registry import AssetProviderRegistry
from app.asset.providers.runtime import AssetProviderRuntime
from app.core.config import settings
from app.asset.providers.pixabay.audio_provider import PixabayAudioProvider

def build_default_asset_provider_registry() -> AssetProviderRegistry:
    registry = AssetProviderRegistry()

    if settings.enable_pexels:
        registry.register(PexelsProvider())

    if settings.enable_pixabay:
        registry.register(PixabayProvider())

    if settings.enable_freesound:
        registry.register(FreesoundProvider())
    
    if settings.enable_pixabay:
        registry.register(PixabayAudioProvider())

    return registry


def build_default_asset_provider_runtime() -> AssetProviderRuntime:
    return AssetProviderRuntime(
        registry=build_default_asset_provider_registry(),
    )