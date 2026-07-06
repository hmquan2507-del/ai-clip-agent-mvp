from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.ai.base.metadata_manager import MetadataManager
from app.editing.execution.graph import DependencyResolver, ExecutionGraphBuilder
from app.repositories.content_graph_repository import ContentGraphRepository


class ExecutionGraphService:
    METADATA_KEY = "execution_graph"

    def __init__(self, db: Session):
        self.content_graph_repository = ContentGraphRepository(db)
        self.builder = ExecutionGraphBuilder()
        self.dependency_resolver = DependencyResolver()

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

        metadata = MetadataManager.load(graph.metadata_json)
        editable_timeline = metadata.get("editable_timeline", {})

        if not isinstance(editable_timeline, dict):
            editable_timeline = {}

        execution_graph = self.builder.build(
            production_id=str(production_id),
            editable_timeline=editable_timeline,
        )

        validation_errors = self.dependency_resolver.validate(execution_graph)
        execution_graph.metadata["validation_errors"] = validation_errors
        execution_graph.metadata["is_valid"] = len(validation_errors) == 0

        result = execution_graph.to_dict()

        metadata[self.METADATA_KEY] = result

        self.content_graph_repository.update_metadata_json(
            graph_id=str(graph.id),
            metadata_json=json.dumps(metadata, ensure_ascii=False),
        )

        return result