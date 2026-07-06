from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.composition_runtime_service import CompositionRuntimeService

router = APIRouter(
    prefix="/productions",
    tags=["Composition Runtime"],
)


@router.post("/{production_id}/composition/run")
def run_composition_runtime(
    production_id: UUID,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    service = CompositionRuntimeService(db)
    return service.run(production_id=production_id)