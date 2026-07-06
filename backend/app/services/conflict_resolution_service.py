from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.artifacts.keys import OPTIMIZED_EXECUTION_GRAPH, TIMELINE
from app.artifacts.runtime_store import RuntimeArtifactStore
from app.editing.execution.conflict import (
    ConflictDetector,
    ConflictResolver,
    GraphOptimizer,
)
from app.editing.execution.graph.graph_builder import ExecutionGraphBuilder
from app.repositories.content_graph_repository import ContentGraphRepository


class ConflictResolutionService:
    def __init__(self, db: Session):
        self.content_graph_repository = ContentGraphRepository(db)
        self.artifact_store = RuntimeArtifactStore(db)
        self.graph_builder = ExecutionGraphBuilder()
        self.detector = ConflictDetector()
        self.resolver = ConflictResolver()
        self.optimizer = GraphOptimizer()

    def run(self, production_id: UUID) -> dict[str, Any]:
        graph_model = self.content_graph_repository.get_latest_by_production(
            production_id=str(production_id)
        )

        if graph_model is None:
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

        execution_graph = self.graph_builder.build(
            production_id=str(production_id),
            editable_timeline=editable_timeline,
        )

        conflicts = self.detector.detect(execution_graph)

        resolved_graph, resolutions = self.resolver.resolve(
            graph=execution_graph,
            conflicts=conflicts,
        )

        optimized_graph = self.optimizer.optimize(resolved_graph)

        optimized_graph.metadata["conflict_count"] = len(conflicts)
        optimized_graph.metadata["resolution_count"] = len(resolutions)
        optimized_graph.metadata["conflicts"] = [
            conflict.to_dict() for conflict in conflicts
        ]
        optimized_graph.metadata["resolutions"] = [
            resolution.to_dict() for resolution in resolutions
        ]

        result = optimized_graph.to_dict()

        self.artifact_store.save(
            production_id=str(production_id),
            artifact_key=OPTIMIZED_EXECUTION_GRAPH,
            payload=result,
        )

        return result