from __future__ import annotations

from app.asset.providers.models import AssetProviderSearchResult


def map_freesound_item(item: dict) -> AssetProviderSearchResult:
    previews = item.get("previews") or {}

    return AssetProviderSearchResult(
        provider_key="freesound",
        provider_asset_id=str(item.get("id")),
        asset_type="sound_effect",
        title=item.get("name"),
        description=item.get("description"),
        remote_url=previews.get("preview-hq-mp3") or previews.get("preview-lq-mp3"),
        thumbnail_url=None,
        preview_url=item.get("url"),
        duration=float(item.get("duration") or 0),
        width=None,
        height=None,
        license=item.get("license"),
        tags=item.get("tags") or [],
        metadata={
            "username": item.get("username"),
            "source_url": item.get("url"),
            "raw": item,
        },
    )