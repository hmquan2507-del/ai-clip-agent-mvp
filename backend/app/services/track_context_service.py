from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.ai.base.metadata_manager import MetadataManager
from app.editing.track.track_context_builder import TrackContextBuilder
from app.repositories.content_graph_repository import ContentGraphRepository


class TrackContextService:
    METADATA_KEY = "track_context"

    def __init__(self, db: Session):
        self.content_graph_repository = ContentGraphRepository(db)
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

        metadata = MetadataManager.load(graph.metadata_json)

        optimized_execution_graph = metadata.get("optimized_execution_graph", {})
        if not isinstance(optimized_execution_graph, dict):
            optimized_execution_graph = {}

        context = self.builder.build(
            production_id=str(production_id),
            optimized_execution_graph=optimized_execution_graph,
        )

        result = context.to_dict()
        metadata[self.METADATA_KEY] = result

        self.content_graph_repository.update_metadata_json(
            graph_id=str(graph.id),
            metadata_json=json.dumps(metadata, ensure_ascii=False),
        )

        return result