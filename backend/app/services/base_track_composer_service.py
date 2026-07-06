from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.ai.base.metadata_manager import MetadataManager
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

        metadata = MetadataManager.load(graph.metadata_json)

        track_context_payload = metadata.get("track_context", {})
        if not isinstance(track_context_payload, dict):
            track_context_payload = {}

        context = self.context_loader.load(
            production_id=str(production_id),
            payload=track_context_payload,
        )

        kwargs = self.build_kwargs(graph=graph, metadata=metadata)

        result = self.runtime.run_composer(
            track_key=self.TRACK_KEY,
            composer=self.composer,
            context=context,
            **kwargs,
        )

        result_dict = result.to_dict()
        metadata[self.METADATA_KEY] = result_dict["payload"]

        self.content_graph_repository.update_metadata_json(
            graph_id=str(graph.id),
            metadata_json=json.dumps(metadata, ensure_ascii=False),
        )

        return result_dict["payload"]

    def build_kwargs(
        self,
        graph: Any,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        return {}