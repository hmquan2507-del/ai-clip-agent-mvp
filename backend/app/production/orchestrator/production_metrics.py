from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter
from typing import Any

from app.production.contracts import PipelineStage


@dataclass
class StageMetric:
    stage: PipelineStage
    duration_ms: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage.value,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
        }


class ProductionMetrics:
    def __init__(self):
        self.started_at = perf_counter()
        self.stage_started_at: dict[PipelineStage, float] = {}
        self.stage_metrics: list[StageMetric] = []

    def start_stage(self, stage: PipelineStage) -> None:
        self.stage_started_at[stage] = perf_counter()

    def finish_stage(
        self,
        stage: PipelineStage,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        started_at = self.stage_started_at.get(stage)

        if started_at is None:
            return

        duration_ms = round((perf_counter() - started_at) * 1000, 2)

        self.stage_metrics.append(
            StageMetric(
                stage=stage,
                duration_ms=duration_ms,
                metadata=metadata or {},
            )
        )

    def total_duration_ms(self) -> float:
        return round((perf_counter() - self.started_at) * 1000, 2)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_duration_ms": self.total_duration_ms(),
            "stages": [item.to_dict() for item in self.stage_metrics],
        }