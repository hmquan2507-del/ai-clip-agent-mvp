from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.production.contracts import PipelineResult, PipelineStage, PipelineStatus


@dataclass
class ProductionRetryResult:
    production_id: str
    stage: PipelineStage
    status: PipelineStatus
    result: PipelineResult | None = None
    attempts: int = 0
    retried: bool = False
    retry_reasons: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_success(self) -> bool:
        return self.status == PipelineStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        return self.status == PipelineStatus.FAILED

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "stage": self.stage.value,
            "status": self.status.value,
            "result": self.result.to_dict() if self.result else None,
            "attempts": self.attempts,
            "retried": self.retried,
            "retry_reasons": self.retry_reasons,
            "metadata": self.metadata,
        }