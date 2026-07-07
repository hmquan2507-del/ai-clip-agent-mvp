from __future__ import annotations

from app.production.events.event import ProductionEvent
from app.production.events.event_handler import ProductionEventHandler
from app.production.metrics.production_metrics_runtime import ProductionMetricsRuntime


class MetricsRuntimeEventHandler(ProductionEventHandler):
    def __init__(self, runtime: ProductionMetricsRuntime):
        self.runtime = runtime

    def handle(
        self,
        event: ProductionEvent,
    ) -> None:
        self.runtime.handle_event(event)

    def to_dict(self) -> dict:
        return self.runtime.to_dict()