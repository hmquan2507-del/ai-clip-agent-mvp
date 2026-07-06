from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.render_schedule_service import RenderScheduleService

router = APIRouter(
    prefix="/productions",
    tags=["Render Schedule"],
)


@router.post("/{production_id}/render-schedule/run")
def run_render_schedule(
    production_id: UUID,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    service = RenderScheduleService(db)
    return service.run(production_id=production_id)