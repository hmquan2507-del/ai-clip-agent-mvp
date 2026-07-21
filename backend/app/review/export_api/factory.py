from __future__ import annotations

from fastapi import APIRouter

from app.review.export_api.controller import create_export_workspace_router
from app.review.export_api.service import ExportWorkspaceApplicationService
from app.review.render.submission.factory import (
    create_render_job_submission_runtime,
)
from app.services.queue_service import QueueService


def create_export_workspace_application_service(
    queue_service: QueueService,
) -> ExportWorkspaceApplicationService:
    return ExportWorkspaceApplicationService(
        create_render_job_submission_runtime(queue_service)
    )


def create_export_workspace_api_router(
    queue_service_provider,
) -> APIRouter:
    return create_export_workspace_router(
        lambda: create_export_workspace_application_service(
            queue_service_provider()
        )
    )
