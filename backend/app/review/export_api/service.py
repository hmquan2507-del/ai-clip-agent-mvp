from __future__ import annotations

from app.review.export_api.schemas import (
    ExportRenderContractRequest,
    ExportSubmissionData,
    ExportSubmissionResponse,
)
from app.review.render.contracts import ReviewRenderContract
from app.review.render.submission.runtime import RenderJobSubmissionRuntime


class ExportWorkspaceApplicationService:
    """Application boundary used by the Export Workspace controller."""

    def __init__(self, submission_runtime: RenderJobSubmissionRuntime):
        self.submission_runtime = submission_runtime

    def submit_render(
        self,
        request: ExportRenderContractRequest,
    ) -> ExportSubmissionResponse:
        contract = ReviewRenderContract(
            contract_version=request.contract_version,
            snapshot_id=request.snapshot_id,
            production_id=request.production_id,
            timeline_revision=request.timeline_revision,
            timeline=request.timeline,
            created_at=request.created_at,
            render_options=request.render_options,
            metadata=request.metadata,
            checksum=request.checksum,
        )

        result = self.submission_runtime.try_submit(
            contract,
            requested_by=request.requested_by,
            correlation_id=request.correlation_id,
        )

        if not result.success or result.receipt is None:
            return ExportSubmissionResponse(
                success=False,
                error_code=result.error_code or "render_submission_failed",
                error=result.error or "Render submission failed.",
            )

        receipt = result.receipt
        return ExportSubmissionResponse(
            success=True,
            data=ExportSubmissionData(
                queue_job_id=receipt.queue_job_id,
                production_id=receipt.production_id,
                snapshot_id=receipt.snapshot_id,
                timeline_revision=receipt.timeline_revision,
                idempotency_key=receipt.idempotency_key,
                duplicate=receipt.duplicate,
            ),
        )
