from __future__ import annotations

from app.render.production.runtime import (
    ProductionRenderRuntime,
)


def build_production_render_runtime() -> (
    ProductionRenderRuntime
):
    return ProductionRenderRuntime()