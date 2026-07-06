from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.artifacts.keys import TIMELINE
from app.artifacts.runtime_store import RuntimeArtifactStore
from app.editing.timeline.timeline_composer import TimelineComposer
from app.repositories.content_graph_repository import ContentGraphRepository


class TimelineComposerService:
    def __init__(self, db: Session):
        self.content_graph_repository = ContentGraphRepository(db)
        self.artifact_store = RuntimeArtifactStore(db)
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

        execution_plan = self.artifact_store.load_payload(
            production_id=str(production_id),
            artifact_key="editing_execution_planner",
            default={},
        )

        instructions = execution_plan.get("instructions", [])
        if not isinstance(instructions, list):
            instructions = []

        timeline = self.composer.compose(
            production_id=str(production_id),
            instructions=[item for item in instructions if isinstance(item, dict)],
            duration=self._infer_duration_from_graph(graph),
        )

        result = timeline.to_dict()

        self.artifact_store.save(
            production_id=str(production_id),
            artifact_key=TIMELINE,
            payload=result,
        )

        return result

    def _infer_duration_from_graph(self, graph: Any) -> float | None:
        if not getattr(graph, "segments", None):
            return None

        end_times: list[float] = []

        for segment in graph.segments:
            try:
                end_times.append(float(segment.end_time))
            except (TypeError, ValueError):
                continue

        return max(end_times) if end_times else None