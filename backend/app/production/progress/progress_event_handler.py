from __future__ import annotations

from app.production.events.event import ProductionEvent
from app.production.events.event_handler import ProductionEventHandler
from app.production.progress.production_progress_runtime import ProductionProgressRuntime


class ProgressRuntimeEventHandler(ProductionEventHandler):
    def __init__(self, runtime: ProductionProgressRuntime):
        self.runtime = runtime

    def handle(
        self,
        event: ProductionEvent,
    ) -> None:
        self.runtime.handle_event(event)

    def to_dict(self) -> dict:
        return self.runtime.to_dict()