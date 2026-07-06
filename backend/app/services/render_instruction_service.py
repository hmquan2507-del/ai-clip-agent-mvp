from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.artifacts.runtime_store import RuntimeArtifactStore
from app.render.instruction.runtime import RenderInstructionRuntime
from app.repositories.content_graph_repository import ContentGraphRepository


class RenderInstructionService:
    def __init__(self, db: Session):
        self.content_graph_repository = ContentGraphRepository(db)
        self.artifact_store = RuntimeArtifactStore(db)
        self.runtime = RenderInstructionRuntime()

    def run(self, production_id: UUID) -> dict[str, Any]:
        graph = self.content_graph_repository.get_latest_by_production(
            production_id=str(production_id)
        )

        if graph is None:
            return {
                "production_id": str(production_id),
                "instructions": [],
                "metadata": {
                    "status": "skipped",
                    "reason": "content_graph_not_found",
                },
            }

        composition = self.artifact_store.load_composition(str(production_id))

        instruction_set = self.runtime.run(
            production_id=str(production_id),
            composition=composition,
        )

        result = instruction_set.to_dict()

        self.artifact_store.save_render_instructions(
            production_id=str(production_id),
            payload=result,
        )

        return result