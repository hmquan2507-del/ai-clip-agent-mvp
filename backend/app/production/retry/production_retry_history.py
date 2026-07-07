from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.production.contracts import PipelineStage, PipelineStatus


@dataclass
class ProductionRetryHistoryItem:
    stage: PipelineStage
    attempt: int
    status: PipelineStatus
    reason: str
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage.value,
            "attempt": self.attempt,
            "status": self.status.value,
            "reason": self.reason,
            "error": self.error,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }