from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.production.contracts import PipelineStage, PipelineStatus


@dataclass
class PipelineHistoryItem:
    stage: PipelineStage
    status: PipelineStatus
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage.value,
            "status": self.status.value,
            "error": self.error,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }