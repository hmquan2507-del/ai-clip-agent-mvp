from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.artifacts.runtime_store import RuntimeArtifactStore
from app.artifacts.validator import RuntimeArtifactValidator


class RuntimeArtifactValidationService:
    def __init__(self, db: Session):
        self.artifact_store = RuntimeArtifactStore(db)
        self.validator = RuntimeArtifactValidator()

    def run(self, production_id: UUID | str) -> dict[str, Any]:
        rows = self.artifact_store.list(str(production_id))

        latest_by_key = {}

        for row in rows:
            current = latest_by_key.get(row.artifact_key)

            if current is None:
                latest_by_key[row.artifact_key] = row
                continue

            current_version = current.artifact_version or 0
            row_version = row.artifact_version or 0

            if row_version > current_version:
                latest_by_key[row.artifact_key] = row

        artifacts = {
            key: row.payload
            for key, row in latest_by_key.items()
        }

        result = self.validator.validate(
            production_id=str(production_id),
            artifacts=artifacts,
        )

        result["artifacts"] = [
            {
                "artifact_key": row.artifact_key,
                "artifact_version": row.artifact_version,
                "checksum": row.checksum,
            }
            for row in latest_by_key.values()
        ]

        return result