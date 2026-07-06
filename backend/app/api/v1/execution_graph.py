from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.execution_graph_service import ExecutionGraphService

router = APIRouter(
    prefix="/productions",
    tags=["Execution Graph"],
)


@router.post("/{production_id}/execution-graph/run")
def run_execution_graph(
    production_id: UUID,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    service = ExecutionGraphService(db)
    return service.run(production_id=production_id)