from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.review.export_api.schemas import (
    ExportRenderContractRequest,
    ExportSubmissionResponse,
)
from app.review.export_api.service import ExportWorkspaceApplicationService
from app.review.export_api.status import ExportRenderStatusService
from app.review.render.submission.factory import (
    create_render_job_submission_runtime,
)
from app.services.queue_service import QueueService

router = APIRouter(
    prefix="/api/v1/export-workspace",
    tags=["Export Workspace"],
)


def get_queue_service(db: Session = Depends(get_db)) -> QueueService:
    return QueueService(db)


def get_export_workspace_service(
    queue_service: QueueService = Depends(get_queue_service),
) -> ExportWorkspaceApplicationService:
    return ExportWorkspaceApplicationService(
        create_render_job_submission_runtime(queue_service)
    )


def get_export_render_status_service(
    queue_service: QueueService = Depends(get_queue_service),
) -> ExportRenderStatusService:
    return ExportRenderStatusService(queue_service)


@router.post(
    "/render-submissions",
    response_model=ExportSubmissionResponse,
    status_code=202,
    summary="Submit an immutable review render contract",
)
def submit_render(
    request: ExportRenderContractRequest,
    service: ExportWorkspaceApplicationService = Depends(
        get_export_workspace_service
    ),
) -> ExportSubmissionResponse:
    return service.submit_render(request)


@router.get(
    "/render-submissions/{queue_job_id}",
    summary="Get render submission status",
)
def get_render_status(
    queue_job_id: UUID,
    service: ExportRenderStatusService = Depends(
        get_export_render_status_service
    ),
) -> dict:
    return {
        "success": True,
        "data": service.get_status(queue_job_id),
    }


@router.get("/health", summary="Export Workspace API health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "component": "export-workspace-api",
        "version": "16.8.4",
    }
