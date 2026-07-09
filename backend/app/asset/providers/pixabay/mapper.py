from __future__ import annotations

from app.asset.providers.models import AssetProviderSearchResult


def map_pixabay_video(item: dict) -> AssetProviderSearchResult:
    videos = item.get("videos") or {}
    medium = videos.get("medium") or videos.get("large") or videos.get("small") or {}

    tags = []
    if item.get("tags"):
        tags = [tag.strip() for tag in str(item["tags"]).split(",") if tag.strip()]

    return AssetProviderSearchResult(
        provider_key="pixabay",
        provider_asset_id=str(item.get("id")),
        asset_type="broll",
        title=f"Pixabay video {item.get('id')}",
        description=item.get("pageURL"),
        remote_url=medium.get("url"),
        thumbnail_url=item.get("picture_id"),
        preview_url=item.get("pageURL"),
        duration=float(item.get("duration") or 0),
        width=medium.get("width"),
        height=medium.get("height"),
        license="pixabay",
        tags=tags,
        metadata={
            "source_url": item.get("pageURL"),
            "user": item.get("user"),
            "downloads": item.get("downloads"),
            "likes": item.get("likes"),
            "raw": item,
        },
    )