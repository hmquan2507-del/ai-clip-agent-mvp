from __future__ import annotations

from functools import lru_cache

from fastapi import Depends

from app.product import ProductWorkspaceService
from app.product.api.dependencies import (
    get_product_workspace_service,
)
from app.review.application.factory import (
    build_review_workspace_application_service,
)
from app.review.application.service import (
    ReviewWorkspaceApplicationService,
)
from app.review.session.registry import (
    ReviewRuntimeSessionRegistryInterface,
    build_in_memory_review_runtime_session_registry,
)


@lru_cache(maxsize=1)
def get_review_runtime_session_registry(
) -> ReviewRuntimeSessionRegistryInterface:
    """
    Process-scoped registry.

    Các HTTP request khác nhau phải dùng chung registry
    để không làm mất History, Clipboard và Timeline Store
    của review session đang hoạt động.
    """

    return (
        build_in_memory_review_runtime_session_registry(
            ttl_seconds=1800.0,
        )
    )


def get_review_workspace_application_service(
    product_workspace_service: (
        ProductWorkspaceService
    ) = Depends(
        get_product_workspace_service
    ),
    session_registry: (
        ReviewRuntimeSessionRegistryInterface
    ) = Depends(
        get_review_runtime_session_registry
    ),
) -> ReviewWorkspaceApplicationService:
    """
    Application Service được tạo theo request.

    ProductWorkspaceService tiếp tục dùng database session
    của request hiện tại, trong khi Session Registry được
    dùng chung giữa các request.
    """

    return (
        build_review_workspace_application_service(
            product_workspace_service=(
                product_workspace_service
            ),
            session_registry=session_registry,
        )
    )