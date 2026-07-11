from __future__ import annotations

from pathlib import Path
from typing import Any

from app.product.adapters import (
    ProductSnapshotBuilder,
)
from app.product.workspace.cache import (
    ProductWorkspaceCache,
)
from app.product.workspace.repository.ai_summary import (
    RepositoryAISummaryWorkspaceAdapter,
)
from app.product.workspace.repository.artifact import (
    RepositoryArtifactWorkspaceAdapter,
)
from app.product.workspace.repository.issues import (
    RepositoryIssueWorkspaceAdapter,
)
from app.product.workspace.repository.production import (
    RepositoryProductionWorkspaceAdapter,
)
from app.product.workspace.repository.quality import (
    RepositoryQualityWorkspaceAdapter,
)
from app.product.workspace.repository.timeline import (
    RepositoryTimelineWorkspaceAdapter,
)
from app.product.workspace.service import (
    ProductWorkspaceService,
)


def build_repository_product_workspace_service(
    *,
    production_repository: Any,
    timeline_repository: Any | None = None,
    artifact_repository: Any | None = None,
    quality_repository: Any | None = None,
    ai_repository: Any | None = None,
    issue_repository: Any | None = None,
    storage_roots: list[str | Path]
    | None = None,
    cache_ttl_seconds: float = 15.0,
) -> ProductWorkspaceService:
    production_loader = (
        RepositoryProductionWorkspaceAdapter(
            production_repository
        )
    )

    timeline_loader = (
        RepositoryTimelineWorkspaceAdapter(
            timeline_repository,
            storage_roots=storage_roots,
        )
    )

    artifact_loader = (
        RepositoryArtifactWorkspaceAdapter(
            artifact_repository,
            storage_roots=storage_roots,
        )
    )

    quality_loader = (
        RepositoryQualityWorkspaceAdapter(
            quality_repository,
            storage_roots=storage_roots,
        )
    )

    ai_summary_loader = (
        RepositoryAISummaryWorkspaceAdapter(
            ai_repository
        )
    )

    issue_loader = (
        RepositoryIssueWorkspaceAdapter(
            issue_repository,
            quality_loader=quality_loader,
        )
    )

    return ProductWorkspaceService(
        production_loader=(
            production_loader
        ),
        timeline_loader=timeline_loader,
        artifact_loader=artifact_loader,
        quality_loader=quality_loader,
        ai_summary_loader=(
            ai_summary_loader
        ),
        issue_loader=issue_loader,
        snapshot_builder=(
            ProductSnapshotBuilder()
        ),
        cache=ProductWorkspaceCache(
            ttl_seconds=cache_ttl_seconds
        ),
    )