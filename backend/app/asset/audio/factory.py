from __future__ import annotations

from app.asset.audio.runtime import AudioProviderRuntime


def build_audio_provider_runtime() -> AudioProviderRuntime:
    return AudioProviderRuntime()