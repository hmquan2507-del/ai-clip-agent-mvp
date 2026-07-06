from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.artifacts.runtime_store import RuntimeArtifactStore
from app.render.assets.asset_resolver import AssetResolver
from app.repositories.content_graph_repository import ContentGraphRepository


class AssetResolverService:
    def __init__(self, db: Session):
        self.content_graph_repository = ContentGraphRepository(db)
        self.artifact_store = RuntimeArtifactStore(db)
        self.resolver = AssetResolver()

    def run(self, production_id: UUID) -> dict[str, Any]:
        graph = self.content_graph_repository.get_latest_by_production(
            production_id=str(production_id)
        )

        if graph is None:
            return {
                "production_id": str(production_id),
                "assets": [],
                "output_path": None,
                "metadata": {
                    "status": "skipped",
                    "reason": "content_graph_not_found",
                },
            }

        artifact_metadata = {
            "composition": self.artifact_store.load_composition(str(production_id)),
            "subtitle_track": self.artifact_store.load_subtitle_track(
                str(production_id)
            ),
            "video_track": self.artifact_store.load_video_track(str(production_id)),
            "audio_track": self.artifact_store.load_audio_track(str(production_id)),
            "render_schedule": self.artifact_store.load_render_schedule(
                str(production_id)
            ),
        }

        resolved_assets = self.resolver.resolve(
            production_id=str(production_id),
            metadata=artifact_metadata,
        )

        result = resolved_assets.to_dict()

        self.artifact_store.save_resolved_assets(
            production_id=str(production_id),
            payload=result,
        )

        return result