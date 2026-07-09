from __future__ import annotations

from app.asset.providers.models import AssetProviderSearchResult


def map_pixabay_audio(
    item: dict,
    asset_type: str,
) -> AssetProviderSearchResult:
    tags = []

    if item.get("tags"):
        tags = [
            tag.strip()
            for tag in str(item.get("tags")).split(",")
            if tag.strip()
        ]

    audio_url = (
        item.get("audio")
        or item.get("audioURL")
        or item.get("previewURL")
        or item.get("downloadURL")
    )

    return AssetProviderSearchResult(
        provider_key="pixabay_audio",
        provider_asset_id=str(item.get("id")),
        asset_type=asset_type,
        title=item.get("name") or f"Pixabay audio {item.get('id')}",
        description=item.get("pageURL"),
        remote_url=audio_url,
        thumbnail_url=None,
        preview_url=item.get("pageURL"),
        duration=float(item.get("duration") or 0),
        width=None,
        height=None,
        license="pixabay",
        tags=tags,
        metadata={
            "source_url": item.get("pageURL"),
            "user": item.get("user"),
            "genre": item.get("genre"),
            "downloads": item.get("downloads"),
            "likes": item.get("likes"),
            "raw": item,
        },
    )