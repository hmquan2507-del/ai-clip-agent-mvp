from __future__ import annotations

from app.product.workspace.service import ProductWorkspaceService
from app.review.application.service import (
    ReviewWorkspaceApplicationConfig,
    ReviewWorkspaceApplicationService,
)
from app.review.session.registry import (
    ReviewRuntimeSessionRegistryInterface,
    build_in_memory_review_runtime_session_registry,
)


def build_review_workspace_application_service(
    *,
    product_workspace_service: ProductWorkspaceService,
    session_registry: (
        ReviewRuntimeSessionRegistryInterface | None
    ) = None,
    registry_ttl_seconds: float = 1800.0,
    config: ReviewWorkspaceApplicationConfig | None = None,
) -> ReviewWorkspaceApplicationService:
    registry = session_registry

    if registry is None:
        registry = (
            build_in_memory_review_runtime_session_registry(
                ttl_seconds=registry_ttl_seconds,
            )
        )

    return ReviewWorkspaceApplicationService(
        product_workspace_service=product_workspace_service,
        session_registry=registry,
        config=config,
    )