from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.production.contracts import PipelineStage, PipelineStatus


@dataclass
class ProductionProgress:
    production_id: str
    total_stages: int
    completed_stages: int = 0
    current_stage: PipelineStage | None = None
    status: PipelineStatus = PipelineStatus.PENDING
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def percent(self) -> float:
        if self.total_stages <= 0:
            return 0.0

        return round((self.completed_stages / self.total_stages) * 100, 2)

    def mark_running(self, stage: PipelineStage) -> None:
        self.current_stage = stage
        self.status = PipelineStatus.RUNNING

    def mark_completed_stage(self) -> None:
        self.completed_stages += 1

    def mark_done(self) -> None:
        self.current_stage = None
        self.status = PipelineStatus.COMPLETED
        self.completed_stages = self.total_stages

    def mark_failed(self, stage: PipelineStage) -> None:
        self.current_stage = stage
        self.status = PipelineStatus.FAILED

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "total_stages": self.total_stages,
            "completed_stages": self.completed_stages,
            "current_stage": self.current_stage.value if self.current_stage else None,
            "status": self.status.value,
            "percent": self.percent,
            "metadata": self.metadata,
        }