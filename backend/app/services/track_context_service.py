from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.artifacts.keys import OPTIMIZED_EXECUTION_GRAPH, TRACK_CONTEXT
from app.artifacts.runtime_store import RuntimeArtifactStore
from app.editing.track.track_context_builder import TrackContextBuilder
from app.repositories.content_graph_repository import ContentGraphRepository


class TrackContextService:
    def __init__(self, db: Session):
        self.content_graph_repository = ContentGraphRepository(db)
        self.artifact_store = RuntimeArtifactStore(db)
        self.builder = TrackContextBuilder()

    def run(self, production_id: UUID) -> dict[str, Any]:
        graph = self.content_graph_repository.get_latest_by_production(
            production_id=str(production_id)
        )

        if graph is None:
            return {
                "production_id": str(production_id),
                "metadata": {
                    "status": "skipped",
                    "reason": "content_graph_not_found",
                },
            }

        optimized_execution_graph = self.artifact_store.load_payload(
            production_id=str(production_id),
            artifact_key=OPTIMIZED_EXECUTION_GRAPH,
            default={},
        )

        context = self.builder.build(
            production_id=str(production_id),
            optimized_execution_graph=optimized_execution_graph,
        )

        result = context.to_dict()

        self.artifact_store.save(
            production_id=str(production_id),
            artifact_key=TRACK_CONTEXT,
            payload=result,
        )

        return result