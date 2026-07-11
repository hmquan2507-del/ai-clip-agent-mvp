from __future__ import annotations

from app.product.adapters import (
    ProductSnapshotBuilder,
)
from app.product.workspace.cache import (
    ProductWorkspaceCache,
)
from app.product.workspace.loaders import (
    InMemoryProductWorkspaceLoader,
)
from app.product.workspace.service import (
    ProductWorkspaceService,
)


def build_in_memory_product_workspace_service(
    *,
    ttl_seconds: float = 15.0,
) -> tuple[
    ProductWorkspaceService,
    InMemoryProductWorkspaceLoader,
]:
    loader = (
        InMemoryProductWorkspaceLoader()
    )

    service = ProductWorkspaceService(
        production_loader=loader,
        timeline_loader=loader,
        artifact_loader=loader,
        quality_loader=loader,
        ai_summary_loader=loader,
        issue_loader=loader,
        snapshot_builder=(
            ProductSnapshotBuilder()
        ),
        cache=ProductWorkspaceCache(
            ttl_seconds=ttl_seconds
        ),
    )

    return service, loader