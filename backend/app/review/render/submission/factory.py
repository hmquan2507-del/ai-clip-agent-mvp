from __future__ import annotations

from sqlalchemy.orm import Session

from app.review.render.submission.adapters import QueueServiceRenderSubmissionAdapter
from app.review.render.submission.runtime import RenderJobSubmissionRuntime
from app.services.queue_service import QueueService


def create_render_job_submission_runtime(
    queue_service: QueueService,
    *,
    db: Session | None = None,
) -> RenderJobSubmissionRuntime:
    return RenderJobSubmissionRuntime(
        QueueServiceRenderSubmissionAdapter(queue_service, db=db)
    )
