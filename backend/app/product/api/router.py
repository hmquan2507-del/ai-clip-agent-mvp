from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from app.product import (
    ProductWorkspaceLoadError,
    ProductWorkspaceNotFoundError,
    ProductWorkspaceService,
)
from app.product.api.dependencies import (
    get_product_workspace_service,
)


router = APIRouter(
    prefix="/productions",
    tags=["Product Workspace"],
)


@router.get(
    "/{production_id}/workspace",
    response_model=dict[str, Any],
    summary="Lấy không gian chỉnh sửa video",
    description=(
        "Trả về dữ liệu sản phẩm đã được chuẩn hóa gồm dự án, "
        "tiến độ, timeline, preview, artifacts, chất lượng, "
        "phân tích AI và các thao tác được phép."
    ),
)
def get_product_workspace(
    production_id: UUID,
    force_refresh: bool = Query(
        default=False,
        description=(
            "Bỏ qua cache và tải lại dữ liệu từ database "
            "và storage."
        ),
    ),
    include_timeline_tracks: bool = Query(
        default=True,
        description=(
            "Có trả toàn bộ track và clip của timeline hay không."
        ),
    ),
    service: ProductWorkspaceService = Depends(
        get_product_workspace_service
    ),
) -> dict[str, Any]:
    try:
        snapshot = service.load_workspace(
            production_id=str(production_id),
            force_refresh=force_refresh,
            include_timeline_tracks=include_timeline_tracks,
        )

        return snapshot.to_dict()

    except ProductWorkspaceNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "production_not_found",
                "message": (
                    "Không tìm thấy dự án video."
                ),
                "technical_message": str(error),
                "production_id": str(production_id),
            },
        ) from error

    except ProductWorkspaceLoadError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "workspace_load_failed",
                "message": (
                    "Không thể tải không gian chỉnh sửa video."
                ),
                "technical_message": str(error),
                "production_id": str(production_id),
            },
        ) from error


@router.get(
    "/{production_id}/workspace/summary",
    response_model=dict[str, Any],
    summary="Lấy thông tin tóm tắt dự án",
)
def get_product_workspace_summary(
    production_id: UUID,
    force_refresh: bool = Query(
        default=False,
    ),
    service: ProductWorkspaceService = Depends(
        get_product_workspace_service
    ),
) -> dict[str, Any]:
    """
    Lightweight endpoint for Dashboard and project cards.

    Timeline tracks are excluded so the response remains small.
    """

    try:
        snapshot = service.load_workspace(
            production_id=str(production_id),
            force_refresh=force_refresh,
            include_timeline_tracks=False,
        )

        payload = snapshot.to_dict()

        return {
            "production": payload["production"],
            "timeline": payload["timeline"],
            "preview": payload["preview"],
            "quality": payload["quality"],
            "artifact_count": len(
                payload["artifacts"]
            ),
            "issue_count": len(
                payload["issues"]
            ),
            "metadata": {
                "contract_version": "16.0.5",
                "summary": True,
            },
        }

    except ProductWorkspaceNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "production_not_found",
                "message": (
                    "Không tìm thấy dự án video."
                ),
                "technical_message": str(error),
                "production_id": str(production_id),
            },
        ) from error

    except ProductWorkspaceLoadError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "workspace_load_failed",
                "message": (
                    "Không thể tải thông tin dự án."
                ),
                "technical_message": str(error),
                "production_id": str(production_id),
            },
        ) from error