from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.runtime_artifact_cleanup_service import (
    RuntimeArtifactCleanupService,
)

router = APIRouter(
    prefix="/productions",
    tags=["Runtime Artifact Cleanup"],
)


@router.delete("/{production_id}/runtime-artifacts")
def delete_runtime_artifacts(
    production_id: UUID,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    service = RuntimeArtifactCleanupService(db)
    return service.delete_by_production(production_id)