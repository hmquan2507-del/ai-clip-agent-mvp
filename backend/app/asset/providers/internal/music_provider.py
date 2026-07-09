from __future__ import annotations

from pathlib import Path

from app.asset.providers.base import BaseAssetProvider
from app.asset.providers.models import (
    AssetProviderHealthResult,
    AssetProviderSearchRequest,
    AssetProviderSearchResponse,
    AssetProviderSearchResult,
)


class InternalMusicProvider(BaseAssetProvider):
    provider_key = "internal_music"

    def __init__(
        self,
        music_root: str = "storage/assets/music/internal",
    ):
        self.music_root = Path(music_root)

    def search(
        self,
        request: AssetProviderSearchRequest,
    ) -> AssetProviderSearchResponse:
        results: list[AssetProviderSearchResult] = []

        if not self.music_root.exists():
            return AssetProviderSearchResponse(
                provider_key=self.provider_key,
                query=request.query,
                results=[],
                metadata={"status": "missing_music_root"},
            )

        files = [
            path
            for path in self.music_root.iterdir()
            if path.is_file() and path.suffix.lower() in {".mp3", ".wav", ".ogg", ".m4a"}
        ]

        query_tokens = self._tokens(request.query)
        scored_files = []

        for path in files:
            name_tokens = self._tokens(path.stem)
            overlap = query_tokens.intersection(name_tokens)
            score = len(overlap)

            scored_files.append((score, path, name_tokens))

        scored_files.sort(key=lambda item: item[0], reverse=True)

        for score, path, name_tokens in scored_files[: request.per_page]:
            results.append(
                AssetProviderSearchResult(
                    provider_key=self.provider_key,
                    provider_asset_id=path.stem,
                    asset_type=request.asset_type,
                    title=path.stem,
                    description=str(path),
                    remote_url=str(path),
                    thumbnail_url=None,
                    preview_url=str(path),
                    duration=None,
                    width=None,
                    height=None,
                    license="internal",
                    tags=list(name_tokens),
                    metadata={
                        "source": "internal_music_library",
                        "local_file": True,
                        "match_score": score,
                    },
                )
            )

        return AssetProviderSearchResponse(
            provider_key=self.provider_key,
            query=request.query,
            results=results,
            metadata={
                "status": "ok",
                "file_count": len(files),
                "result_count": len(results),
            },
        )

    def health(self) -> AssetProviderHealthResult:
        return AssetProviderHealthResult(
            provider_key=self.provider_key,
            enabled=True,
            configured=True,
            healthy=self.music_root.exists(),
            missing=[] if self.music_root.exists() else [str(self.music_root)],
            metadata={"music_root": str(self.music_root)},
        )

    def download(self, asset, **kwargs):
        return asset

    def _tokens(self, text: str) -> set[str]:
        normalized = (
            text.lower()
            .replace("-", " ")
            .replace("_", " ")
            .replace(".", " ")
        )

        return {
            item.strip()
            for item in normalized.split()
            if item.strip()
        }