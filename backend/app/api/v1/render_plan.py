from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.render_plan_service import RenderPlanService

router = APIRouter(
    prefix="/productions",
    tags=["Render Plan"],
)


@router.post("/{production_id}/render-plan/run")
def run_render_plan(
    production_id: UUID,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    service = RenderPlanService(db)
    return service.run(production_id=production_id)