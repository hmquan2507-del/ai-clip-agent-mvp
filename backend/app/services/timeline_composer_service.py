from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.ai.base.metadata_manager import MetadataManager
from app.editing.timeline.timeline_composer import TimelineComposer
from app.repositories.content_graph_repository import ContentGraphRepository


class TimelineComposerService:
    METADATA_KEY = "editable_timeline"

    def __init__(self, db: Session):
        self.db = db
        self.content_graph_repository = ContentGraphRepository(db)
        self.composer = TimelineComposer()

    def run(self, production_id: UUID) -> dict[str, Any]:
        graph = self.content_graph_repository.get_latest_by_production(
            production_id=str(production_id)
        )

        if graph is None:
            return {
                "production_id": str(production_id),
                "timeline": None,
                "metadata": {
                    "status": "skipped",
                    "reason": "content_graph_not_found",
                },
            }

        metadata = MetadataManager.load(graph.metadata_json)

        execution_plan = metadata.get("editing_execution_planner", {})
        instructions = execution_plan.get("instructions", [])

        if not isinstance(instructions, list):
            instructions = []

        timeline = self.composer.compose(
            production_id=str(production_id),
            instructions=[
                item for item in instructions if isinstance(item, dict)
            ],
            duration=self._infer_duration_from_graph(graph),
        )

        timeline_dict = timeline.to_dict()

        metadata[self.METADATA_KEY] = timeline_dict

        self.content_graph_repository.update_metadata_json(
            graph_id=str(graph.id),
            metadata_json=json.dumps(metadata, ensure_ascii=False),
        )

        return timeline_dict

    def _infer_duration_from_graph(self, graph: Any) -> float | None:
        if not getattr(graph, "segments", None):
            return None

        end_times: list[float] = []

        for segment in graph.segments:
            try:
                end_times.append(float(segment.end_time))
            except (TypeError, ValueError):
                continue

        if not end_times:
            return None

        return max(end_times)