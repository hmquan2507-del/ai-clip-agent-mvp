from __future__ import annotations

from collections import defaultdict

from app.production.events.event import ProductionEvent
from app.production.events.event_handler import ProductionEventHandler
from app.production.events.event_types import ProductionEventType


class ProductionEventBus:
    def __init__(self):
        self._handlers: dict[
            ProductionEventType,
            list[ProductionEventHandler],
        ] = defaultdict(list)

    def subscribe(
        self,
        event_type: ProductionEventType,
        handler: ProductionEventHandler,
    ) -> None:
        self._handlers[event_type].append(handler)

    def unsubscribe(
        self,
        event_type: ProductionEventType,
        handler: ProductionEventHandler,
    ) -> None:
        if handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)

    def publish(
        self,
        event: ProductionEvent,
    ) -> None:
        for handler in self._handlers[event.event_type]:
            handler.handle(event)