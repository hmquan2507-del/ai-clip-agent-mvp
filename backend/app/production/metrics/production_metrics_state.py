from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class StageMetric:
    stage: str
    duration_ms: float


@dataclass
class ProductionMetricsState:
    production_id: str

    stage_metrics: list[StageMetric] = field(default_factory=list)

    total_duration_ms: float = 0

    retry_count: int = 0

    completed_count: int = 0

    failed_count: int = 0

    skipped_count: int = 0

    artifact_count: int = 0

    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "production_id": self.production_id,
            "stage_metrics": [
                {
                    "stage": x.stage,
                    "duration_ms": x.duration_ms,
                }
                for x in self.stage_metrics
            ],
            "total_duration_ms": self.total_duration_ms,
            "retry_count": self.retry_count,
            "completed_count": self.completed_count,
            "failed_count": self.failed_count,
            "skipped_count": self.skipped_count,
            "artifact_count": self.artifact_count,
            "metadata": self.metadata,
        }