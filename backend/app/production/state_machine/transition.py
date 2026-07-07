from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.production.contracts import PipelineStage, PipelineStatus


@dataclass
class PipelineTransition:
    production_id: str
    current_stage: PipelineStage | None
    next_stage: PipelineStage | None
    status: PipelineStatus
    reason: str
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def has_next(self) -> bool:
        return self.next_stage is not None

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "current_stage": self.current_stage.value if self.current_stage else None,
            "next_stage": self.next_stage.value if self.next_stage else None,
            "status": self.status.value,
            "reason": self.reason,
            "metadata": self.metadata,
        }