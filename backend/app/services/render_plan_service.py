from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.artifacts.runtime_store import RuntimeArtifactStore
from app.render.plan.render_plan_builder import RenderPlanBuilder
from app.repositories.content_graph_repository import ContentGraphRepository


class RenderPlanService:
    def __init__(self, db: Session):
        self.content_graph_repository = ContentGraphRepository(db)
        self.artifact_store = RuntimeArtifactStore(db)
        self.builder = RenderPlanBuilder()

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

        render_instructions = self.artifact_store.load_render_instructions(
            str(production_id)
        )

        render_plan = self.builder.build(
            production_id=str(production_id),
            render_instructions=render_instructions,
        )

        result = render_plan.to_dict()

        self.artifact_store.save_render_plan(
            production_id=str(production_id),
            payload=result,
        )

        return result