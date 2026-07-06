from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.services.execution_graph_service import ExecutionGraphService


class ExecutionGraphWorker:
    def __init__(self, db: Session):
        self.service = ExecutionGraphService(db)

    def run(self, production_id: UUID) -> dict[str, Any]:
        return self.service.run(production_id=production_id)