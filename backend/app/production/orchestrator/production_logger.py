from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.production.contracts import PipelineStage, PipelineStatus


@dataclass
class ProductionLogItem:
    stage: PipelineStage | None
    status: PipelineStatus
    message: str
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage.value if self.stage else None,
            "status": self.status.value,
            "message": self.message,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }


class ProductionLogger:
    def __init__(self):
        self.items: list[ProductionLogItem] = []

    def log(
        self,
        stage: PipelineStage | None,
        status: PipelineStatus,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.items.append(
            ProductionLogItem(
                stage=stage,
                status=status,
                message=message,
                metadata=metadata or {},
            )
        )

    def to_list(self) -> list[dict[str, Any]]:
        return [item.to_dict() for item in self.items]