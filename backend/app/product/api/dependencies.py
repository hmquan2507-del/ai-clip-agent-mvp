from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.enums import AssetType
from app.db.models.production_asset import ProductionAsset
from app.db.session import get_db
from app.product import (
    ProductWorkspaceService,
    build_repository_product_workspace_service,
)
from app.repositories.content_graph_repository import (
    ContentGraphRepository,
)
from app.repositories.production_repository import (
    ProductionRepository,
)
from app.repositories.runtime_artifact_repository import (
    RuntimeArtifactRepository,
)
from app.repositories.timeline_repository import (
    TimelineRepository,
)

_UPLOAD_BASE_PATH = Path("data/uploads")


def _build_default_source_lookup(
    db: Session,
):
    def lookup(production_id: str) -> dict[str, Any] | None:
        asset = (
            db.query(ProductionAsset)
            .filter(
                ProductionAsset.production_id == production_id,
                ProductionAsset.type == AssetType.SOURCE_VIDEO,
            )
            .order_by(ProductionAsset.created_at.desc())
            .first()
        )

        if asset is None:
            return None

        return {
            "asset_id": str(asset.id),
            "local_path": str(
                (_UPLOAD_BASE_PATH / asset.storage_path).resolve()
            ),
            "duration": asset.duration,
            "width": asset.width,
            "height": asset.height,
            "fps": asset.fps,
        }

    return lookup


def get_product_workspace_service(
    db: Session = Depends(get_db),
) -> ProductWorkspaceService:
    """
    Build one ProductWorkspaceService per API request.

    SQLAlchemy repositories share the request-scoped database session.
    Timeline, render artifact and quality fallback files are read from
    the production storage directories. When a production has no real
    timeline yet, the timeline loader defaults to one clip spanning the
    production's real uploaded source video (see
    RepositoryTimelineWorkspaceAdapter.default_source_lookup) rather than
    an empty or unrelated one.
    """

    return build_repository_product_workspace_service(
        production_repository=ProductionRepository(db),
        timeline_repository=TimelineRepository(db),
        artifact_repository=RuntimeArtifactRepository(db),
        quality_repository=None,
        ai_repository=ContentGraphRepository(db),
        issue_repository=None,
        storage_roots=[
            "storage/render_end_to_end_demo",
            "storage/render_execution_integration",
            "storage/production_render",
            "storage/render_quality_test",
        ],
        cache_ttl_seconds=15.0,
        default_source_lookup=_build_default_source_lookup(db),
    )