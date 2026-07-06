from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.artifacts.runtime_store import RuntimeArtifactStore


class RuntimeArtifactReplayService:
    def __init__(self, db: Session):
        self.artifact_store = RuntimeArtifactStore(db)

    def list_artifacts(self, production_id: UUID) -> dict[str, Any]:
        rows = self.artifact_store.list(str(production_id))

        latest_by_key = {}

        for row in rows:
            current = latest_by_key.get(row.artifact_key)

            if current is None or (
                (row.artifact_version or 0) > (current.artifact_version or 0)
            ):
                latest_by_key[row.artifact_key] = row

        return {
            "production_id": str(production_id),
            "artifacts": [
                {
                    "artifact_key": row.artifact_key,
                    "artifact_version": row.artifact_version,
                    "checksum": row.checksum,
                    "metadata": row.metadata,
                }
                for row in latest_by_key.values()
            ],
            "metadata": {
                "service": "runtime_artifact_replay_service",
                "artifact_count": len(latest_by_key),
            },
        }

    def load_artifact(
        self,
        production_id: UUID,
        artifact_key: str,
    ) -> dict[str, Any]:
        payload = self.artifact_store.load_payload(
            production_id=str(production_id),
            artifact_key=artifact_key,
            default={},
        )

        return {
            "production_id": str(production_id),
            "artifact_key": artifact_key,
            "payload": payload,
        }