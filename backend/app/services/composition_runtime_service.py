from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.ai.base.metadata_manager import MetadataManager
from app.editing.composition.composition_runtime import CompositionRuntime
from app.repositories.content_graph_repository import ContentGraphRepository


class CompositionRuntimeService:
    METADATA_KEY = "composition"

    def __init__(self, db: Session):
        self.content_graph_repository = ContentGraphRepository(db)
        self.runtime = CompositionRuntime()

    def run(self, production_id: UUID) -> dict[str, Any]:
        graph = self.content_graph_repository.get_latest_by_production(
            production_id=str(production_id)
        )

        if graph is None:
            return {
                "production_id": str(production_id),
                "layers": [],
                "render_order": [],
                "metadata": {
                    "status": "skipped",
                    "reason": "content_graph_not_found",
                },
            }

        metadata = MetadataManager.load(graph.metadata_json)

        composition = self.runtime.compose(
            production_id=str(production_id),
            metadata=metadata,
        )

        result = composition.to_dict()
        metadata[self.METADATA_KEY] = result

        self.content_graph_repository.update_metadata_json(
            graph_id=str(graph.id),
            metadata_json=json.dumps(metadata, ensure_ascii=False),
        )

        return result