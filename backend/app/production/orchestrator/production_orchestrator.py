from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.artifacts.runtime_store import RuntimeArtifactStore
from app.production.contracts import (
    PipelineExecutionContext,
    PipelineResult,
    PipelineStatus,
)
from app.production.events.event import ProductionEvent
from app.production.events.event_runtime import (
    ProductionEventRuntime,
    build_production_event_runtime,
)
from app.production.events.event_types import ProductionEventType
from app.production.orchestrator.production_executor import ProductionExecutor
from app.production.orchestrator.production_summary import ProductionSummary
from app.production.registry import (
    DEFAULT_PIPELINE_STAGES,
    build_default_pipeline_registry,
)
from app.production.state_machine import ProductionStateMachine


class ProductionOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.registry = build_default_pipeline_registry()
        self.state_machine = ProductionStateMachine(DEFAULT_PIPELINE_STAGES)
        self.executor = ProductionExecutor(self.registry)

    def run(
        self,
        production_id: UUID,
        mode: str = "gemini",
    ) -> dict[str, Any]:
        production_id_str = str(production_id)

        context = PipelineExecutionContext(
            production_id=production_id,
            db=self.db,
            artifact_store=RuntimeArtifactStore(self.db),
            mode=mode,
        )

        event_runtime = build_production_event_runtime(
            production_id=production_id_str,
            total_stages=len(DEFAULT_PIPELINE_STAGES),
        )

        history: list[dict[str, Any]] = []

        self._publish(
            event_runtime=event_runtime,
            event_type=ProductionEventType.PRODUCTION_STARTED,
            production_id=production_id_str,
            metadata={
                "mode": mode,
                "stage_count": len(DEFAULT_PIPELINE_STAGES),
            },
        )

        transition = self.state_machine.first_stage(production_id_str)

        while transition.has_next:
            stage = transition.next_stage

            if stage is None:
                break

            self._publish(
                event_runtime=event_runtime,
                event_type=ProductionEventType.STAGE_STARTED,
                production_id=production_id_str,
                stage=stage.value,
                metadata={
                    "mode": mode,
                },
            )

            result = self.executor.run_stage(
                stage=stage,
                context=context,
            )

            history_item = self.state_machine.build_history_item(result)
            history.append(history_item.to_dict())

            event_type = self._event_type_for_result(result)

            self._publish(
                event_runtime=event_runtime,
                event_type=event_type,
                production_id=production_id_str,
                stage=stage.value,
                metadata={
                    "artifact_key": result.artifact_key,
                    "error": result.error,
                    "result_status": result.status.value,
                    "runner_metadata": result.metadata,
                },
            )

            if result.status == PipelineStatus.FAILED:
                self._publish(
                    event_runtime=event_runtime,
                    event_type=ProductionEventType.PRODUCTION_FAILED,
                    production_id=production_id_str,
                    stage=stage.value,
                    metadata={
                        "failed_stage": stage.value,
                        "error": result.error,
                        "mode": mode,
                    },
                )

                return self._summary(
                    production_id=production_id_str,
                    status=PipelineStatus.FAILED,
                    event_runtime=event_runtime,
                    history=history,
                    metadata={
                        "failed_stage": stage.value,
                        "error": result.error,
                        "mode": mode,
                    },
                )

            transition = self.state_machine.transition_after_result(result)

        self._publish(
            event_runtime=event_runtime,
            event_type=ProductionEventType.PRODUCTION_COMPLETED,
            production_id=production_id_str,
            metadata={
                "stage_count": len(DEFAULT_PIPELINE_STAGES),
                "mode": mode,
            },
        )

        return self._summary(
            production_id=production_id_str,
            status=PipelineStatus.COMPLETED,
            event_runtime=event_runtime,
            history=history,
            metadata={
                "stage_count": len(DEFAULT_PIPELINE_STAGES),
                "mode": mode,
            },
        )

    def _event_type_for_result(
        self,
        result: PipelineResult,
    ) -> ProductionEventType:
        if result.status == PipelineStatus.COMPLETED:
            return ProductionEventType.STAGE_COMPLETED

        if result.status == PipelineStatus.SKIPPED:
            return ProductionEventType.STAGE_SKIPPED

        if result.status == PipelineStatus.FAILED:
            return ProductionEventType.STAGE_FAILED

        if result.status == PipelineStatus.CANCELLED:
            return ProductionEventType.STAGE_FAILED

        return ProductionEventType.STAGE_COMPLETED

    def _publish(
        self,
        event_runtime: ProductionEventRuntime,
        event_type: ProductionEventType,
        production_id: str,
        stage: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        event_runtime.bus.publish(
            ProductionEvent(
                event_type=event_type,
                production_id=production_id,
                stage=stage,
                metadata=metadata or {},
            )
        )

    def _summary(
        self,
        production_id: str,
        status: PipelineStatus,
        event_runtime: ProductionEventRuntime,
        history: list[dict[str, Any]],
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        return ProductionSummary(
            production_id=production_id,
            status=status,
            progress=event_runtime.progress.to_dict(),
            metrics=event_runtime.metrics.to_dict(),
            logs=event_runtime.logger.events,
            history=history,
            metadata=metadata,
        ).to_dict()