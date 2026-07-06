from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.render_instruction_service import RenderInstructionService

router = APIRouter(
    prefix="/productions",
    tags=["Render Instruction"],
)


@router.post("/{production_id}/render-instructions/run")
def run_render_instructions(
    production_id: UUID,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    service = RenderInstructionService(db)
    return service.run(production_id=production_id)