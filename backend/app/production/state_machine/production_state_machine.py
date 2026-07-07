from __future__ import annotations

from app.production.contracts import PipelineResult, PipelineStage, PipelineStatus
from app.production.state_machine.history import PipelineHistoryItem
from app.production.state_machine.transition import PipelineTransition
from app.production.state_machine.validator import ProductionStateMachineValidator


class ProductionStateMachine:
    def __init__(
        self,
        stages: list[PipelineStage],
    ):
        self.stages = stages
        self.validator = ProductionStateMachineValidator()

        errors = self.validator.validate_pipeline(stages)
        if errors:
            raise ValueError(f"Invalid production pipeline: {errors}")

    def first_stage(
        self,
        production_id: str,
    ) -> PipelineTransition:
        return PipelineTransition(
            production_id=production_id,
            current_stage=None,
            next_stage=self.stages[0],
            status=PipelineStatus.PENDING,
            reason="pipeline_start",
            metadata={
                "stage_count": len(self.stages),
            },
        )

    def next_after(
        self,
        production_id: str,
        current_stage: PipelineStage,
    ) -> PipelineTransition:
        index = self._index_of(current_stage)

        if index is None:
            return PipelineTransition(
                production_id=production_id,
                current_stage=current_stage,
                next_stage=None,
                status=PipelineStatus.FAILED,
                reason="current_stage_not_in_pipeline",
            )

        next_index = index + 1

        if next_index >= len(self.stages):
            return PipelineTransition(
                production_id=production_id,
                current_stage=current_stage,
                next_stage=None,
                status=PipelineStatus.COMPLETED,
                reason="pipeline_completed",
            )

        return PipelineTransition(
            production_id=production_id,
            current_stage=current_stage,
            next_stage=self.stages[next_index],
            status=PipelineStatus.PENDING,
            reason="next_stage_resolved",
            metadata={
                "current_index": index,
                "next_index": next_index,
                "stage_count": len(self.stages),
            },
        )

    def transition_after_result(
        self,
        result: PipelineResult,
    ) -> PipelineTransition:
        if result.status == PipelineStatus.FAILED:
            return PipelineTransition(
                production_id=result.production_id,
                current_stage=result.stage,
                next_stage=None,
                status=PipelineStatus.FAILED,
                reason="stage_failed",
                metadata={
                    "error": result.error,
                    "artifact_key": result.artifact_key,
                },
            )

        if result.status == PipelineStatus.CANCELLED:
            return PipelineTransition(
                production_id=result.production_id,
                current_stage=result.stage,
                next_stage=None,
                status=PipelineStatus.CANCELLED,
                reason="stage_cancelled",
                metadata={
                    "artifact_key": result.artifact_key,
                },
            )

        return self.next_after(
            production_id=result.production_id,
            current_stage=result.stage,
        )

    def build_history_item(
        self,
        result: PipelineResult,
    ) -> PipelineHistoryItem:
        return PipelineHistoryItem(
            stage=result.stage,
            status=result.status,
            error=result.error,
            metadata={
                "artifact_key": result.artifact_key,
                **result.metadata,
            },
        )

    def _index_of(
        self,
        stage: PipelineStage,
    ) -> int | None:
        try:
            return self.stages.index(stage)
        except ValueError:
            return None