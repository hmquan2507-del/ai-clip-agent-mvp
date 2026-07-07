from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.production.contracts.pipeline_stage import PipelineStage
from app.production.contracts.pipeline_status import PipelineStatus


@dataclass
class PipelineResult:
    production_id: str
    stage: PipelineStage
    status: PipelineStatus
    payload: dict[str, Any] = field(default_factory=dict)
    artifact_key: str | None = None
    error: str | None = None
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
            "payload": self.payload,
            "artifact_key": self.artifact_key,
            "error": self.error,
            "metadata": self.metadata,
        }