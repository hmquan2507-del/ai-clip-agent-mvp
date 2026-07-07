from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.production.contracts import PipelineStatus


@dataclass
class ProductionSummary:
    production_id: str
    status: PipelineStatus
    progress: dict[str, Any]
    metrics: dict[str, Any]
    logs: list[dict[str, Any]]
    history: list[dict[str, Any]]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "status": self.status.value,
            "progress": self.progress,
            "metrics": self.metrics,
            "logs": self.logs,
            "history": self.history,
            "metadata": self.metadata,
        }