from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.production.contracts.pipeline_stage import PipelineStage
from app.production.contracts.pipeline_status import PipelineStatus


@dataclass
class PipelineEvent:
    production_id: str
    stage: PipelineStage
    status: PipelineStatus
    message: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "stage": self.stage.value,
            "status": self.status.value,
            "message": self.message,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }