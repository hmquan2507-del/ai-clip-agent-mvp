from __future__ import annotations

from app.production.contracts import PipelineStatus


class ProductionResumePolicy:

    def should_resume(
        self,
        status: PipelineStatus,
    ) -> bool:

        return status in (
            PipelineStatus.FAILED,
            PipelineStatus.RUNNING,
        )