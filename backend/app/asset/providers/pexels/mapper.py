from __future__ import annotations

from app.asset.providers.models import AssetProviderSearchResult


def map_pexels_video(item: dict) -> AssetProviderSearchResult:
    video_files = item.get("video_files") or []
    video_pictures = item.get("video_pictures") or []

    best_file = video_files[0] if video_files else {}

    return AssetProviderSearchResult(
        provider_key="pexels",
        provider_asset_id=str(item.get("id")),
        asset_type="broll",
        title=f"Pexels video {item.get('id')}",
        description=item.get("url"),
        remote_url=best_file.get("link"),
        thumbnail_url=(video_pictures[0].get("picture") if video_pictures else None),
        preview_url=item.get("url"),
        duration=float(item.get("duration") or 0),
        width=item.get("width"),
        height=item.get("height"),
        license="pexels",
        tags=[],
        metadata={
            "source_url": item.get("url"),
            "photographer": item.get("user", {}).get("name") if isinstance(item.get("user"), dict) else None,
            "raw": item,
        },
    )