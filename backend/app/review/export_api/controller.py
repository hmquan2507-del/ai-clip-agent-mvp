from __future__ import annotations

from collections.abc import Callable

from fastapi import APIRouter, Depends, status

from app.review.export_api.schemas import (
    ExportRenderContractRequest,
    ExportSubmissionResponse,
)
from app.review.export_api.service import ExportWorkspaceApplicationService


def create_export_workspace_router(
    service_provider: Callable[[], ExportWorkspaceApplicationService],
) -> APIRouter:
    router = APIRouter(
        prefix="/api/v1/export-workspace",
        tags=["Export Workspace"],
    )

    def get_service() -> ExportWorkspaceApplicationService:
        return service_provider()

    @router.post(
        "/render-submissions",
        response_model=ExportSubmissionResponse,
        status_code=status.HTTP_202_ACCEPTED,
        summary="Submit an immutable review render contract",
    )
    def submit_render(
        request: ExportRenderContractRequest,
        service: ExportWorkspaceApplicationService = Depends(get_service),
    ) -> ExportSubmissionResponse:
        return service.submit_render(request)

    @router.get(
        "/health",
        summary="Export Workspace API health",
    )
    def health() -> dict[str, str]:
        return {
            "status": "ok",
            "component": "export-workspace-api",
            "version": "16.8.3",
        }

    return router
