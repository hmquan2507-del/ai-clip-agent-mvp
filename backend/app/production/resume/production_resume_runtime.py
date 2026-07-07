from __future__ import annotations

from app.production.contracts import PipelineStage, PipelineStatus
from app.production.resume.production_checkpoint import ProductionCheckpoint
from app.production.resume.production_resume_policy import ProductionResumePolicy
from app.production.resume.production_resume_result import ProductionResumeResult
from app.production.state_machine.history import PipelineHistoryItem


class ProductionResumeRuntime:
    def __init__(self):
        self.policy = ProductionResumePolicy()
        self.checkpoint = ProductionCheckpoint()

    def resolve(
        self,
        production_id: str,
        stages: list[PipelineStage],
        history: list[PipelineHistoryItem],
    ) -> ProductionResumeResult:
        if not history:
            return ProductionResumeResult(
                production_id=production_id,
                should_resume=True,
                resume_stage=stages[0],
                completed_stages=[],
                remaining_stages=stages,
                metadata={"reason": "pipeline_not_started"},
            )

        last = history[-1]

        if last.status == PipelineStatus.COMPLETED:
            index = stages.index(last.stage)

            if index == len(stages) - 1:
                return ProductionResumeResult(
                    production_id=production_id,
                    should_resume=False,
                    resume_stage=None,
                    completed_stages=stages,
                    remaining_stages=[],
                    metadata={"reason": "pipeline_completed"},
                )

            return ProductionResumeResult(
                production_id=production_id,
                should_resume=True,
                resume_stage=stages[index + 1],
                completed_stages=stages[: index + 1],
                remaining_stages=stages[index + 1 :],
                metadata={"reason": "resume_next_stage"},
            )

        if self.policy.should_resume(last.status):
            index = stages.index(last.stage)

            return ProductionResumeResult(
                production_id=production_id,
                should_resume=True,
                resume_stage=last.stage,
                completed_stages=stages[:index],
                remaining_stages=stages[index:],
                metadata={"reason": "resume_failed_stage"},
            )

        return ProductionResumeResult(
            production_id=production_id,
            should_resume=False,
            resume_stage=None,
            completed_stages=[],
            remaining_stages=[],
            metadata={"reason": "resume_not_allowed"},
        )