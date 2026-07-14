from __future__ import annotations

from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Query,
    status,
)
from fastapi.responses import JSONResponse

from app.review.api.contracts import (
    ReviewWorkspaceAPIErrorCode,
    ReviewWorkspaceAPIOperation,
)
from app.review.api.dependencies import (
    get_review_workspace_application_service,
)
from app.review.api.mappers import (
    ReviewWorkspaceAPIMapper,
)
from app.review.api.schemas import (
    CloseReviewWorkspaceRequest,
    OpenReviewWorkspaceRequest,
    ResetReviewWorkspaceRequest,
    ReviewWorkspaceCloseResponse,
    ReviewWorkspaceResetResponse,
    ReviewWorkspaceSessionResponse,
    ReviewWorkspaceSnapshotResponse,
)
from app.review.application.service import (
    ReviewWorkspaceApplicationService,
)


router = APIRouter(
    prefix=(
        "/productions/"
        "{production_id}/review"
    ),
    tags=["Review Workspace"],
)


@router.post(
    "/session",
    response_model=(
        ReviewWorkspaceSessionResponse
    ),
    status_code=status.HTTP_200_OK,
    summary="Mở phiên review workspace",
)
def open_review_session(
    production_id: UUID,
    request: OpenReviewWorkspaceRequest,
    service: (
        ReviewWorkspaceApplicationService
    ) = Depends(
        get_review_workspace_application_service
    ),
) -> (
    ReviewWorkspaceSessionResponse
    | JSONResponse
):
    normalized_id = str(production_id)

    try:
        session = service.open_session(
            normalized_id,
            force_refresh=(
                request.force_refresh
            ),
            replace_existing=(
                request.replace_existing
            ),
        )

        return (
            ReviewWorkspaceAPIMapper
            .session_response(
                session,
                operation=(
                    ReviewWorkspaceAPIOperation
                    .OPEN_SESSION
                ),
            )
        )

    except Exception as error:
        return _error_response(
            error,
            production_id=normalized_id,
        )


@router.get(
    "/session",
    response_model=(
        ReviewWorkspaceSessionResponse
    ),
    summary=(
        "Lấy phiên review đang hoạt động"
    ),
)
def get_review_session(
    production_id: UUID,
    session_id: str | None = Query(
        default=None,
        min_length=1,
        max_length=128,
    ),
    service: (
        ReviewWorkspaceApplicationService
    ) = Depends(
        get_review_workspace_application_service
    ),
) -> (
    ReviewWorkspaceSessionResponse
    | JSONResponse
):
    normalized_id = str(production_id)

    try:
        session = service.get_session(
            normalized_id,
            session_id=session_id,
        )

        return (
            ReviewWorkspaceAPIMapper
            .session_response(
                session,
                operation=(
                    ReviewWorkspaceAPIOperation
                    .GET_SESSION
                ),
            )
        )

    except Exception as error:
        return _error_response(
            error,
            production_id=normalized_id,
            session_id=session_id,
        )


@router.get(
    "/snapshot",
    response_model=(
        ReviewWorkspaceSnapshotResponse
    ),
    summary=(
        "Lấy snapshot review workspace"
    ),
)
def get_review_snapshot(
    production_id: UUID,
    session_id: str | None = Query(
        default=None,
        min_length=1,
        max_length=128,
    ),
    service: (
        ReviewWorkspaceApplicationService
    ) = Depends(
        get_review_workspace_application_service
    ),
) -> (
    ReviewWorkspaceSnapshotResponse
    | JSONResponse
):
    normalized_id = str(production_id)

    try:
        snapshot = service.get_snapshot(
            normalized_id,
            session_id=session_id,
        )

        return (
            ReviewWorkspaceAPIMapper
            .snapshot_response(snapshot)
        )

    except Exception as error:
        return _error_response(
            error,
            production_id=normalized_id,
            session_id=session_id,
        )


@router.post(
    "/reset",
    response_model=(
        ReviewWorkspaceResetResponse
    ),
    summary=(
        "Reset phiên review về timeline ban đầu"
    ),
)
def reset_review_session(
    production_id: UUID,
    request: ResetReviewWorkspaceRequest,
    service: (
        ReviewWorkspaceApplicationService
    ) = Depends(
        get_review_workspace_application_service
    ),
) -> (
    ReviewWorkspaceResetResponse
    | JSONResponse
):
    normalized_id = str(production_id)

    try:
        snapshot = service.reset_session(
            normalized_id,
            session_id=request.session_id,
        )

        return (
            ReviewWorkspaceAPIMapper
            .reset_response(snapshot)
        )

    except Exception as error:
        return _error_response(
            error,
            production_id=normalized_id,
            session_id=request.session_id,
        )


@router.delete(
    "/session",
    response_model=(
        ReviewWorkspaceCloseResponse
    ),
    summary=(
        "Đóng phiên review workspace"
    ),
)
def close_review_session(
    production_id: UUID,
    request: CloseReviewWorkspaceRequest,
    service: (
        ReviewWorkspaceApplicationService
    ) = Depends(
        get_review_workspace_application_service
    ),
) -> (
    ReviewWorkspaceCloseResponse
    | JSONResponse
):
    normalized_id = str(production_id)

    try:
        result = service.close_session(
            normalized_id,
            session_id=request.session_id,
        )

        return (
            ReviewWorkspaceAPIMapper
            .close_response(result)
        )

    except Exception as error:
        return _error_response(
            error,
            production_id=normalized_id,
            session_id=request.session_id,
        )


def _error_response(
    error: Exception,
    *,
    production_id: str | None = None,
    session_id: str | None = None,
) -> JSONResponse:
    response = (
        ReviewWorkspaceAPIMapper
        .error_response(
            error,
            production_id=production_id,
            session_id=session_id,
        )
    )

    return JSONResponse(
        status_code=(
            _status_code_for_error(error)
        ),
        content=response.model_dump(
            mode="json"
        ),
    )


def _status_code_for_error(
    error: Exception,
) -> int:
    response = (
        ReviewWorkspaceAPIMapper
        .error_response(error)
    )

    code = response.error.code

    if code in {
        (
            ReviewWorkspaceAPIErrorCode
            .PRODUCTION_NOT_FOUND
        ),
        (
            ReviewWorkspaceAPIErrorCode
            .SESSION_NOT_FOUND
        ),
    }:
        return status.HTTP_404_NOT_FOUND

    if code in {
        (
            ReviewWorkspaceAPIErrorCode
            .SESSION_CONFLICT
        ),
        (
            ReviewWorkspaceAPIErrorCode
            .SESSION_OPERATION_FAILED
        ),
    }:
        return status.HTTP_409_CONFLICT

    if (
        code
        == (
            ReviewWorkspaceAPIErrorCode
            .VALIDATION_ERROR
        )
    ):
        return (
            status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    return (
        status.HTTP_500_INTERNAL_SERVER_ERROR
    )