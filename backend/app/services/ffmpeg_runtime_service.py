from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.artifacts.runtime_store import RuntimeArtifactStore
from app.render.ffmpeg.ffmpeg_runtime import FFmpegRuntime
from app.repositories.content_graph_repository import ContentGraphRepository


class FFmpegRuntimeService:
    def __init__(self, db: Session):
        self.content_graph_repository = ContentGraphRepository(db)
        self.artifact_store = RuntimeArtifactStore(db)
        self.runtime = FFmpegRuntime()

    def run(self, production_id: UUID) -> dict[str, Any]:
        graph = self.content_graph_repository.get_latest_by_production(
            production_id=str(production_id)
        )

        if graph is None:
            return {
                "production_id": str(production_id),
                "commands": [],
                "metadata": {
                    "status": "skipped",
                    "reason": "content_graph_not_found",
                },
            }

        render_schedule = self.artifact_store.load_render_schedule(
            str(production_id)
        )

        resolved_assets = self.artifact_store.load_resolved_assets(
            str(production_id)
        )

        command_plan = self.runtime.build_command_plan(
            production_id=str(production_id),
            render_schedule=render_schedule,
            resolved_assets=resolved_assets,
        )

        result = command_plan.to_dict()

        self.artifact_store.save_ffmpeg_command_plan(
            production_id=str(production_id),
            payload=result,
        )

        return result