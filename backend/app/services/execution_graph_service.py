from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.artifacts.keys import EXECUTION_GRAPH, TIMELINE
from app.artifacts.runtime_store import RuntimeArtifactStore
from app.editing.execution.graph import DependencyResolver, ExecutionGraphBuilder
from app.repositories.content_graph_repository import ContentGraphRepository


class ExecutionGraphService:
    def __init__(self, db: Session):
        self.content_graph_repository = ContentGraphRepository(db)
        self.artifact_store = RuntimeArtifactStore(db)
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

        editable_timeline = self.artifact_store.load_payload(
            production_id=str(production_id),
            artifact_key=TIMELINE,
            default={},
        )

        execution_graph = self.builder.build(
            production_id=str(production_id),
            editable_timeline=editable_timeline,
        )

        validation_errors = self.dependency_resolver.validate(execution_graph)
        execution_graph.metadata["validation_errors"] = validation_errors
        execution_graph.metadata["is_valid"] = len(validation_errors) == 0

        result = execution_graph.to_dict()

        self.artifact_store.save(
            production_id=str(production_id),
            artifact_key=EXECUTION_GRAPH,
            payload=result,
        )

        return result