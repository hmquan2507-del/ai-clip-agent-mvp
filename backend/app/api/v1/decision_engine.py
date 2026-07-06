from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.decision_engine_service import DecisionEngineService

router = APIRouter(
    prefix="/productions",
    tags=["Decision Engine"],
)


@router.post("/{production_id}/decision-engine/run")
def run_decision_engine(
    production_id: UUID,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    service = DecisionEngineService(db)
    return service.run(production_id=production_id)