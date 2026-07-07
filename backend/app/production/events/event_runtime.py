from __future__ import annotations

from dataclasses import dataclass

from app.production.events.default_handlers import LoggingEventHandler
from app.production.events.event_bus import ProductionEventBus
from app.production.events.event_types import ProductionEventType
from app.production.metrics import MetricsRuntimeEventHandler, ProductionMetricsRuntime
from app.production.progress import ProgressRuntimeEventHandler, ProductionProgressRuntime


@dataclass
class ProductionEventRuntime:
    bus: ProductionEventBus
    logger: LoggingEventHandler
    progress: ProgressRuntimeEventHandler
    metrics: MetricsRuntimeEventHandler


def build_production_event_runtime(
    production_id: str,
    total_stages: int,
) -> ProductionEventRuntime:
    bus = ProductionEventBus()

    logger = LoggingEventHandler()

    progress = ProgressRuntimeEventHandler(
        ProductionProgressRuntime(
            production_id=production_id,
            total_stages=total_stages,
        )
    )

    metrics = MetricsRuntimeEventHandler(
        ProductionMetricsRuntime(
            production_id=production_id,
        )
    )

    for event_type in ProductionEventType:
        bus.subscribe(event_type, logger)
        bus.subscribe(event_type, progress)
        bus.subscribe(event_type, metrics)

    return ProductionEventRuntime(
        bus=bus,
        logger=logger,
        progress=progress,
        metrics=metrics,
    )