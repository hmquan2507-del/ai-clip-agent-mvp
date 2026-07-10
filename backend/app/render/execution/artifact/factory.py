from __future__ import annotations

from app.render.execution.artifact.runtime import (
    RenderArtifactStore,
)


def build_render_artifact_store() -> (
    RenderArtifactStore
):
    return RenderArtifactStore()