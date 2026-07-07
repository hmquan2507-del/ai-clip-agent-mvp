from __future__ import annotations

from app.production.events.event import ProductionEvent
from app.production.events.event_handler import ProductionEventHandler


class LoggingEventHandler(ProductionEventHandler):
    def __init__(self):
        self.events: list[dict] = []

    def handle(self, event: ProductionEvent) -> None:
        self.events.append(event.to_dict())