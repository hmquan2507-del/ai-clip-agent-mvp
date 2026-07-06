from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models.runtime_artifact import RuntimeArtifact


class RuntimeArtifactRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(
        self,
        production_id: str,
        artifact_key: str,
        payload_json: str,
        checksum: str | None = None,
        artifact_version: int | None = None,
    ) -> RuntimeArtifact:
        version = artifact_version or self.next_version(
            production_id=production_id,
            artifact_key=artifact_key,
        )

        artifact = RuntimeArtifact(
            production_id=production_id,
            artifact_key=artifact_key,
            artifact_version=version,
            payload_json=payload_json,
            checksum=checksum,
        )

        self.db.add(artifact)
        self.db.commit()
        self.db.refresh(artifact)

        return artifact

    def load_latest(
        self,
        production_id: str,
        artifact_key: str,
    ) -> RuntimeArtifact | None:
        return (
            self.db.query(RuntimeArtifact)
            .filter(RuntimeArtifact.production_id == production_id)
            .filter(RuntimeArtifact.artifact_key == artifact_key)
            .order_by(RuntimeArtifact.artifact_version.desc())
            .first()
        )

    def load_version(
        self,
        production_id: str,
        artifact_key: str,
        artifact_version: int,
    ) -> RuntimeArtifact | None:
        return (
            self.db.query(RuntimeArtifact)
            .filter(RuntimeArtifact.production_id == production_id)
            .filter(RuntimeArtifact.artifact_key == artifact_key)
            .filter(RuntimeArtifact.artifact_version == artifact_version)
            .first()
        )

    def list_by_production(
        self,
        production_id: str,
    ) -> list[RuntimeArtifact]:
        return (
            self.db.query(RuntimeArtifact)
            .filter(RuntimeArtifact.production_id == production_id)
            .order_by(
                RuntimeArtifact.artifact_key.asc(),
                RuntimeArtifact.artifact_version.desc(),
            )
            .all()
        )

    def list_by_key(
        self,
        production_id: str,
        artifact_key: str,
    ) -> list[RuntimeArtifact]:
        return (
            self.db.query(RuntimeArtifact)
            .filter(RuntimeArtifact.production_id == production_id)
            .filter(RuntimeArtifact.artifact_key == artifact_key)
            .order_by(RuntimeArtifact.artifact_version.desc())
            .all()
        )

    def exists(
        self,
        production_id: str,
        artifact_key: str,
    ) -> bool:
        return self.load_latest(
            production_id=production_id,
            artifact_key=artifact_key,
        ) is not None

    def delete_by_key(
        self,
        production_id: str,
        artifact_key: str,
    ) -> int:
        rows = self.list_by_key(
            production_id=production_id,
            artifact_key=artifact_key,
        )

        count = len(rows)

        for row in rows:
            self.db.delete(row)

        self.db.commit()

        return count

    def delete_by_production(
        self,
        production_id: str,
    ) -> int:
        rows = self.list_by_production(production_id=production_id)
        count = len(rows)

        for row in rows:
            self.db.delete(row)

        self.db.commit()

        return count

    def next_version(
        self,
        production_id: str,
        artifact_key: str,
    ) -> int:
        latest = self.load_latest(
            production_id=production_id,
            artifact_key=artifact_key,
        )

        if latest is None:
            return 1

        return int(latest.artifact_version) + 1