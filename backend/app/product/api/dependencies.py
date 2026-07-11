from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

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


def get_product_workspace_service(
    db: Session = Depends(get_db),
) -> ProductWorkspaceService:
    """
    Build one ProductWorkspaceService per API request.

    SQLAlchemy repositories share the request-scoped database session.
    Timeline, render artifact and quality fallback files are read from
    the production storage directories.
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
    )