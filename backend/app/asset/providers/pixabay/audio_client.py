from __future__ import annotations

import requests

from app.core.config import settings


class PixabayAudioClient:
    audio_url = "https://pixabay.com/api/audio/"

    def search_audio(
        self,
        query: str,
        page: int = 1,
        per_page: int = 10,
    ) -> dict:
        params = {
            "key": settings.pixabay_api_key,
            "q": query,
            "page": page,
            "per_page": per_page,
        }

        response = requests.get(
            self.audio_url,
            params=params,
            timeout=settings.asset_provider_timeout_seconds,
        )
        response.raise_for_status()

        return response.json()