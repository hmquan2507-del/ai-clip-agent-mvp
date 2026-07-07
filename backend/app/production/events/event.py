from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.production.events.event_types import ProductionEventType


@dataclass(slots=True)
class ProductionEvent:
    event_type: ProductionEventType
    production_id: str

    stage: str | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type.value,
            "production_id": self.production_id,
            "stage": self.stage,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }