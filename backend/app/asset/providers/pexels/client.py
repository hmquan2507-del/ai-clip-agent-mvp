from __future__ import annotations

import requests

from app.core.config import settings


class PexelsClient:
    base_url = "https://api.pexels.com"

    def search_videos(
        self,
        query: str,
        page: int = 1,
        per_page: int = 10,
        orientation: str | None = None,
    ) -> dict:
        headers = {"Authorization": settings.pexels_api_key}
        params = {
            "query": query,
            "page": page,
            "per_page": per_page,
        }

        if orientation:
            params["orientation"] = orientation

        response = requests.get(
            f"{self.base_url}/videos/search",
            headers=headers,
            params=params,
            timeout=settings.asset_provider_timeout_seconds,
        )
        response.raise_for_status()
        return response.json()