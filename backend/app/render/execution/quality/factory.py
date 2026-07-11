from __future__ import annotations

from app.render.execution.quality.runtime import (
    RenderQualityGate,
)


def build_render_quality_gate() -> (
    RenderQualityGate
):
    return RenderQualityGate()