from __future__ import annotations

from app.production.contracts import PipelineStatus
from app.production.state_machine.history import PipelineHistoryItem


class ProductionCheckpoint:
    def latest_completed(
        self,
        history: list[PipelineHistoryItem],
    ) -> PipelineHistoryItem | None:
        completed = [
            item
            for item in history
            if item.status == PipelineStatus.COMPLETED
        ]

        if not completed:
            return None

        return completed[-1]