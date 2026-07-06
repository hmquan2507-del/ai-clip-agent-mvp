from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.runtime_artifact_validation_service import (
    RuntimeArtifactValidationService,
)

router = APIRouter(
    prefix="/productions",
    tags=["Runtime Artifact Validation"],
)


@router.get("/{production_id}/runtime-artifacts/validate")
def validate_runtime_artifacts(
    production_id: UUID,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    service = RuntimeArtifactValidationService(db)
    return service.run(production_id=production_id)