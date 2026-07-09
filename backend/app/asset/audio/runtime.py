from __future__ import annotations

from app.asset.audio.models import AudioSearchRequest, AudioSearchResponse
from app.asset.providers import AssetProviderSearchRequest
from app.asset.providers.freesound import FreesoundProvider
from app.asset.providers.pixabay.audio_provider import PixabayAudioProvider


class AudioProviderRuntime:
    def __init__(
        self,
        pixabay_audio_provider: PixabayAudioProvider | None = None,
        freesound_provider: FreesoundProvider | None = None,
    ):
        self.pixabay_audio_provider = pixabay_audio_provider or PixabayAudioProvider()
        self.freesound_provider = freesound_provider or FreesoundProvider()

    def search(
        self,
        request: AudioSearchRequest,
    ) -> list[AudioSearchResponse]:
        providers = self._providers_for_audio_type(request.audio_type)
        responses: list[AudioSearchResponse] = []

        for provider in providers:
            try:
                response = provider.search(
                    AssetProviderSearchRequest(
                        query=request.query,
                        asset_type=request.audio_type,
                        page=request.page,
                        per_page=request.per_page,
                        metadata=request.metadata,
                    )
                )

                responses.append(
                    AudioSearchResponse(
                        provider_key=response.provider_key,
                        query=response.query,
                        audio_type=request.audio_type,
                        results=response.results,
                        metadata=response.metadata,
                    )
                )
            except Exception as error:
                responses.append(
                    AudioSearchResponse(
                        provider_key=getattr(provider, "provider_key", "unknown"),
                        query=request.query,
                        audio_type=request.audio_type,
                        results=[],
                        metadata={
                            "status": "failed",
                            "error": str(error),
                        },
                    )
                )

        return responses

    def _providers_for_audio_type(self, audio_type: str):
        normalized = audio_type.lower()

        if normalized in {"sound_effect", "sfx"}:
            return [
                self.freesound_provider,
                self.pixabay_audio_provider,
            ]

        if normalized == "music":
            return [
                self.pixabay_audio_provider,
            ]

        return [
            self.pixabay_audio_provider,
            self.freesound_provider,
        ]