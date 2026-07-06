from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.ai.base.metadata_manager import MetadataManager
from app.editing.execution.conflict import (
    ConflictDetector,
    ConflictResolver,
    GraphOptimizer,
)
from app.editing.execution.graph.graph_builder import ExecutionGraphBuilder
from app.repositories.content_graph_repository import ContentGraphRepository


class ConflictResolutionService:
    METADATA_KEY = "optimized_execution_graph"

    def __init__(self, db: Session):
        self.content_graph_repository = ContentGraphRepository(db)
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

        metadata = MetadataManager.load(graph_model.metadata_json)
        editable_timeline = metadata.get("editable_timeline", {})

        if not isinstance(editable_timeline, dict):
            editable_timeline = {}

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

        metadata[self.METADATA_KEY] = result

        self.content_graph_repository.update_metadata_json(
            graph_id=str(graph_model.id),
            metadata_json=json.dumps(metadata, ensure_ascii=False),
        )

        return result