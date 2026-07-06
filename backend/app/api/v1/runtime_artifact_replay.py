from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.runtime_artifact_replay_service import (
    RuntimeArtifactReplayService,
)

router = APIRouter(
    prefix="/productions",
    tags=["Runtime Artifact Replay"],
)


@router.get("/{production_id}/runtime-artifacts")
def list_runtime_artifacts(
    production_id: UUID,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    service = RuntimeArtifactReplayService(db)
    return service.list_artifacts(production_id)


@router.get("/{production_id}/runtime-artifacts/{artifact_key}")
def load_runtime_artifact(
    production_id: UUID,
    artifact_key: str,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    service = RuntimeArtifactReplayService(db)
    return service.load_artifact(
        production_id=production_id,
        artifact_key=artifact_key,
    )