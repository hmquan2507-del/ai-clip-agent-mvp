from __future__ import annotations

from app.render.assets.models import RenderAsset


def placeholder_asset(
    asset_id: str,
    asset_type: str,
    reason: str,
) -> RenderAsset:
    return RenderAsset(
        asset_id=asset_id,
        asset_type=asset_type,
        uri=None,
        local_path=None,
        is_placeholder=True,
        metadata={
            "reason": reason,
            "status": "placeholder",
        },
    )