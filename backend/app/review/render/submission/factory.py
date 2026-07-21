from __future__ import annotations

from app.review.render.submission.adapters import QueueServiceRenderSubmissionAdapter
from app.review.render.submission.runtime import RenderJobSubmissionRuntime
from app.services.queue_service import QueueService


def create_render_job_submission_runtime(
    queue_service: QueueService,
) -> RenderJobSubmissionRuntime:
    return RenderJobSubmissionRuntime(
        QueueServiceRenderSubmissionAdapter(queue_service)
    )
