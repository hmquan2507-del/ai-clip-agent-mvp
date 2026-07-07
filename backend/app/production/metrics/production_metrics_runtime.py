from __future__ import annotations

from app.production.events.event import ProductionEvent
from app.production.events.event_types import ProductionEventType
from app.production.metrics.production_metrics_state import (
    ProductionMetricsState,
    StageMetric,
)
from app.production.metrics.stage_timer import StageTimer


class ProductionMetricsRuntime:
    def __init__(self, production_id: str):
        self.state = ProductionMetricsState(production_id=production_id)
        self.timer = StageTimer()

    def handle_event(self, event: ProductionEvent) -> None:
        if event.event_type == ProductionEventType.STAGE_STARTED:
            if event.stage:
                self.timer.start(event.stage)
            return

        if event.event_type == ProductionEventType.STAGE_COMPLETED:
            if event.stage:
                duration = self.timer.stop(event.stage)
                self.state.completed_count += 1
                self.state.stage_metrics.append(
                    StageMetric(stage=event.stage, duration_ms=duration)
                )
                self.state.total_duration_ms += duration
            return

        if event.event_type == ProductionEventType.STAGE_FAILED:
            if event.stage:
                duration = self.timer.stop(event.stage)
                self.state.failed_count += 1
                self.state.stage_metrics.append(
                    StageMetric(stage=event.stage, duration_ms=duration)
                )
                self.state.total_duration_ms += duration
            return

        if event.event_type == ProductionEventType.STAGE_SKIPPED:
            self.state.skipped_count += 1
            return

        if event.event_type == ProductionEventType.STAGE_RETRY:
            self.state.retry_count += 1
            return

    def to_dict(self) -> dict:
        return self.state.to_dict()