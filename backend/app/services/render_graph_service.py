from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.artifacts.runtime_store import RuntimeArtifactStore
from app.render.graph.render_graph_builder import RenderGraphBuilder
from app.render.graph.render_graph_validator import RenderGraphValidator
from app.repositories.content_graph_repository import ContentGraphRepository


class RenderGraphService:
    def __init__(self, db: Session):
        self.content_graph_repository = ContentGraphRepository(db)
        self.artifact_store = RuntimeArtifactStore(db)
        self.builder = RenderGraphBuilder()
        self.validator = RenderGraphValidator()

    def run(self, production_id: UUID) -> dict[str, Any]:
        graph = self.content_graph_repository.get_latest_by_production(
            production_id=str(production_id)
        )

        if graph is None:
            return {
                "production_id": str(production_id),
                "nodes": [],
                "edges": [],
                "metadata": {
                    "status": "skipped",
                    "reason": "content_graph_not_found",
                },
            }

        render_plan = self.artifact_store.load_render_plan(str(production_id))

        render_graph = self.builder.build(
            production_id=str(production_id),
            render_plan=render_plan,
        )

        validation_errors = self.validator.validate(render_graph)

        render_graph.metadata["validation_errors"] = validation_errors
        render_graph.metadata["is_valid"] = len(validation_errors) == 0

        result = render_graph.to_dict()

        self.artifact_store.save_render_graph(
            production_id=str(production_id),
            payload=result,
        )

        return result