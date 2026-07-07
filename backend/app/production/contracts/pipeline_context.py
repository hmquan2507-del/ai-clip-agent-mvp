from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.artifacts.runtime_store import RuntimeArtifactStore


@dataclass
class PipelineExecutionContext:
    production_id: UUID
    db: Session
    artifact_store: RuntimeArtifactStore
    mode: str = "gemini"
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def production_id_str(self) -> str:
        return str(self.production_id)

    def get_artifact(
        self,
        artifact_key: str,
        default: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self.artifact_store.load_payload(
            production_id=self.production_id_str,
            artifact_key=artifact_key,
            default=default or {},
        )

    def save_artifact(
        self,
        artifact_key: str,
        payload: dict[str, Any],
    ) -> None:
        self.artifact_store.save(
            production_id=self.production_id_str,
            artifact_key=artifact_key,
            payload=payload,
        )