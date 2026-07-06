from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.editing_execution_planner_service import (
    EditingExecutionPlannerService,
)

router = APIRouter(
    prefix="/productions",
    tags=["Editing Execution Planner"],
)


@router.post("/{production_id}/editing-execution-planner/run")
def run_editing_execution_planner(
    production_id: UUID,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    service = EditingExecutionPlannerService(db)
    return service.run(production_id=production_id)