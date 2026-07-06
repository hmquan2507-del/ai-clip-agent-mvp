from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.artifacts.runtime_store import RuntimeArtifactStore


class RuntimeArtifactCleanupService:
    def __init__(self, db: Session):
        self.artifact_store = RuntimeArtifactStore(db)

    def delete_by_production(self, production_id: UUID) -> dict[str, Any]:
        deleted = self.artifact_store.delete_by_production(str(production_id))

        return {
            "production_id": str(production_id),
            "deleted_artifacts": deleted,
            "metadata": {
                "service": "runtime_artifact_cleanup_service",
            },
        }