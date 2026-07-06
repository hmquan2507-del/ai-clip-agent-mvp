from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.editing_style_service import EditingStyleService

router = APIRouter(
    prefix="/productions",
    tags=["Editing Style Engine"],
)


@router.post("/{production_id}/editing-style/run")
def run_editing_style(
    production_id: UUID,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    service = EditingStyleService(db)
    return service.run(production_id=production_id)