from __future__ import annotations

from abc import ABC, abstractmethod

from app.production.events.event import ProductionEvent


class ProductionEventHandler(ABC):

    @abstractmethod
    def handle(
        self,
        event: ProductionEvent,
    ) -> None:
        ...