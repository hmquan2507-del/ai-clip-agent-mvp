from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.artifacts.runtime_store import RuntimeArtifactStore
from app.render.scheduler.render_schedule_builder import RenderScheduleBuilder
from app.repositories.content_graph_repository import ContentGraphRepository


class RenderScheduleService:
    def __init__(self, db: Session):
        self.content_graph_repository = ContentGraphRepository(db)
        self.artifact_store = RuntimeArtifactStore(db)
        self.builder = RenderScheduleBuilder()

    def run(self, production_id: UUID) -> dict[str, Any]:
        graph = self.content_graph_repository.get_latest_by_production(
            production_id=str(production_id)
        )

        if graph is None:
            return {
                "production_id": str(production_id),
                "steps": [],
                "metadata": {
                    "status": "skipped",
                    "reason": "content_graph_not_found",
                },
            }

        render_graph = self.artifact_store.load_render_graph(str(production_id))

        render_schedule = self.builder.build(
            production_id=str(production_id),
            render_graph=render_graph,
        )

        result = render_schedule.to_dict()

        self.artifact_store.save_render_schedule(
            production_id=str(production_id),
            payload=result,
        )

        return result