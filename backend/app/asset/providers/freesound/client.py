from __future__ import annotations

import requests

from app.core.config import settings


class FreesoundClient:
    base_url = "https://freesound.org/apiv2"

    def text_search(
        self,
        query: str,
        page: int = 1,
        page_size: int = 10,
    ) -> dict:
        headers = {"Authorization": f"Token {settings.freesound_api_key}"}
        params = {
            "query": query,
            "page": page,
            "page_size": page_size,
            "fields": "id,name,tags,description,duration,license,previews,url,username",
        }

        response = requests.get(
            f"{self.base_url}/search/text/",
            headers=headers,
            params=params,
            timeout=settings.asset_provider_timeout_seconds,
        )
        response.raise_for_status()
        return response.json()