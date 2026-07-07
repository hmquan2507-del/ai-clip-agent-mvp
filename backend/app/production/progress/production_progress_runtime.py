from __future__ import annotations

from app.production.contracts import PipelineStatus
from app.production.events.event import ProductionEvent
from app.production.events.event_types import ProductionEventType
from app.production.progress.production_progress_state import ProductionProgressState


class ProductionProgressRuntime:
    def __init__(self, production_id: str, total_stages: int):
        self.state = ProductionProgressState(
            production_id=production_id,
            total_stages=total_stages,
        )

    def handle_event(self, event: ProductionEvent) -> None:
        if event.event_type == ProductionEventType.PRODUCTION_STARTED:
            self.state.status = PipelineStatus.RUNNING
            self.state.current_stage = None
            return

        if event.event_type == ProductionEventType.STAGE_STARTED:
            self.state.status = PipelineStatus.RUNNING
            self.state.current_stage = event.stage
            return

        if event.event_type == ProductionEventType.STAGE_COMPLETED:
            if event.stage and event.stage not in self.state.completed_stages:
                self.state.completed_stages.append(event.stage)
            self.state.current_stage = None
            return

        if event.event_type == ProductionEventType.STAGE_SKIPPED:
            if event.stage and event.stage not in self.state.skipped_stages:
                self.state.skipped_stages.append(event.stage)
            self.state.current_stage = None
            return

        if event.event_type == ProductionEventType.STAGE_FAILED:
            self.state.status = PipelineStatus.FAILED
            self.state.failed_stage = event.stage
            self.state.current_stage = event.stage
            return

        if event.event_type == ProductionEventType.PRODUCTION_COMPLETED:
            self.state.status = PipelineStatus.COMPLETED
            self.state.current_stage = None
            return

        if event.event_type == ProductionEventType.PRODUCTION_FAILED:
            self.state.status = PipelineStatus.FAILED
            self.state.current_stage = None
            return

    def to_dict(self) -> dict:
        return self.state.to_dict()