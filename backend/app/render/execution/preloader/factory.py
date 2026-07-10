from __future__ import annotations

from app.render.execution.preloader.runtime import (
    RenderAssetPreloader,
)


def build_render_asset_preloader() -> (
    RenderAssetPreloader
):
    return RenderAssetPreloader()