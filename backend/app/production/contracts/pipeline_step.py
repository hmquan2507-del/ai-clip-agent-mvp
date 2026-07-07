from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.production.contracts.pipeline_stage import PipelineStage
from app.production.contracts.pipeline_status import PipelineStatus


@dataclass
class PipelineStep:
    stage: PipelineStage
    status: PipelineStatus = PipelineStatus.PENDING
    order_index: int = 0
    artifact_key: str | None = None
    depends_on: list[PipelineStage] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage.value,
            "status": self.status.value,
            "order_index": self.order_index,
            "artifact_key": self.artifact_key,
            "depends_on": [item.value for item in self.depends_on],
            "metadata": self.metadata,
        }