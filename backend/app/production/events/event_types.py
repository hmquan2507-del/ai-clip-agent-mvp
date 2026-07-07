from __future__ import annotations

from enum import Enum


class ProductionEventType(str, Enum):
    PRODUCTION_STARTED = "production.started"
    PRODUCTION_COMPLETED = "production.completed"
    PRODUCTION_FAILED = "production.failed"

    STAGE_STARTED = "stage.started"
    STAGE_COMPLETED = "stage.completed"
    STAGE_FAILED = "stage.failed"
    STAGE_SKIPPED = "stage.skipped"
    STAGE_RETRY = "stage.retry"