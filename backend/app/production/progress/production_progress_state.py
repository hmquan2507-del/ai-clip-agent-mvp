from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.production.contracts import PipelineStatus


@dataclass
class ProductionProgressState:
    production_id: str
    status: PipelineStatus = PipelineStatus.PENDING
    current_stage: str | None = None
    completed_stages: list[str] = field(default_factory=list)
    failed_stage: str | None = None
    skipped_stages: list[str] = field(default_factory=list)
    total_stages: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def completed_count(self) -> int:
        return len(self.completed_stages)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped_stages)

    @property
    def percent(self) -> float:
        if self.total_stages <= 0:
            return 0.0

        done = self.completed_count + self.skipped_count
        return round((done / self.total_stages) * 100, 2)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "status": self.status.value,
            "current_stage": self.current_stage,
            "completed_stages": self.completed_stages,
            "failed_stage": self.failed_stage,
            "skipped_stages": self.skipped_stages,
            "total_stages": self.total_stages,
            "completed_count": self.completed_count,
            "skipped_count": self.skipped_count,
            "percent": self.percent,
            "metadata": self.metadata,
        }