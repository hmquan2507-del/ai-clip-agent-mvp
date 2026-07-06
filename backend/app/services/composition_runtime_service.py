from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.artifacts.keys import AUDIO_TRACK, COMPOSITION, SUBTITLE_TRACK, VIDEO_TRACK
from app.artifacts.runtime_store import RuntimeArtifactStore
from app.editing.composition.composition_runtime import CompositionRuntime
from app.repositories.content_graph_repository import ContentGraphRepository


class CompositionRuntimeService:
    def __init__(self, db: Session):
        self.content_graph_repository = ContentGraphRepository(db)
        self.artifact_store = RuntimeArtifactStore(db)
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

        metadata = {
            SUBTITLE_TRACK: self.artifact_store.load_payload(
                str(production_id), SUBTITLE_TRACK, {}
            ),
            VIDEO_TRACK: self.artifact_store.load_payload(
                str(production_id), VIDEO_TRACK, {}
            ),
            AUDIO_TRACK: self.artifact_store.load_payload(
                str(production_id), AUDIO_TRACK, {}
            ),
        }

        composition = self.runtime.compose(
            production_id=str(production_id),
            metadata=metadata,
        )

        result = composition.to_dict()

        self.artifact_store.save(
            production_id=str(production_id),
            artifact_key=COMPOSITION,
            payload=result,
        )

        return result