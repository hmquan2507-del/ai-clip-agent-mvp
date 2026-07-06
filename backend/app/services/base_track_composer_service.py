from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.artifacts.keys import TRACK_CONTEXT
from app.artifacts.runtime_store import RuntimeArtifactStore
from app.editing.track.segment_loader import SegmentLoader
from app.editing.track.track_context_loader import TrackContextLoader
from app.editing.track.track_runtime import TrackRuntime
from app.repositories.content_graph_repository import ContentGraphRepository


class BaseTrackComposerService:
    METADATA_KEY: str = ""
    TRACK_KEY: str = ""

    def __init__(self, db: Session, composer: Any):
        if not self.METADATA_KEY:
            raise ValueError("METADATA_KEY is required")

        if not self.TRACK_KEY:
            raise ValueError("TRACK_KEY is required")

        self.content_graph_repository = ContentGraphRepository(db)
        self.artifact_store = RuntimeArtifactStore(db)
        self.composer = composer
        self.context_loader = TrackContextLoader()
        self.segment_loader = SegmentLoader()
        self.runtime = TrackRuntime()

    def run(self, production_id: UUID) -> dict[str, Any]:
        graph = self.content_graph_repository.get_latest_by_production(
            production_id=str(production_id)
        )

        if graph is None:
            return {
                "production_id": str(production_id),
                "track_key": self.TRACK_KEY,
                "payload": {},
                "metadata": {
                    "status": "skipped",
                    "reason": "content_graph_not_found",
                },
            }

        track_context_payload = self.artifact_store.load_payload(
            production_id=str(production_id),
            artifact_key=TRACK_CONTEXT,
            default={},
        )

        context = self.context_loader.load(
            production_id=str(production_id),
            payload=track_context_payload,
        )

        kwargs = self.build_kwargs(graph=graph)

        result = self.runtime.run_composer(
            track_key=self.TRACK_KEY,
            composer=self.composer,
            context=context,
            **kwargs,
        )

        result_dict = result.to_dict()
        payload = result_dict["payload"]

        self.artifact_store.save(
            production_id=str(production_id),
            artifact_key=self.METADATA_KEY,
            payload=payload,
        )

        return payload

    def build_kwargs(
        self,
        graph: Any,
    ) -> dict[str, Any]:
        return {}