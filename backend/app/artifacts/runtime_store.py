from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.artifacts import keys
from app.artifacts.models import RuntimeArtifactPayload
from app.artifacts.registry import ArtifactRegistry
from app.artifacts.serializer import ArtifactSerializer
from app.repositories.runtime_artifact_repository import RuntimeArtifactRepository


class RuntimeArtifactStore:
    def __init__(
        self,
        db: Session,
        serializer: ArtifactSerializer | None = None,
        registry: ArtifactRegistry | None = None,
    ):
        self.repository = RuntimeArtifactRepository(db)
        self.serializer = serializer or ArtifactSerializer()
        self.registry = registry or ArtifactRegistry()

    def save(
        self,
        production_id: str,
        artifact_key: str,
        payload: dict[str, Any],
        artifact_version: int | None = None,
    ) -> RuntimeArtifactPayload:
        payload_json = self.serializer.serialize(payload)
        checksum = self.serializer.checksum(payload_json)

        artifact = self.repository.save(
            production_id=production_id,
            artifact_key=artifact_key,
            payload_json=payload_json,
            checksum=checksum,
            artifact_version=artifact_version,
        )

        return RuntimeArtifactPayload(
            production_id=artifact.production_id,
            artifact_key=artifact.artifact_key,
            artifact_version=artifact.artifact_version,
            checksum=artifact.checksum,
            payload=payload,
            metadata={
                "artifact_id": artifact.id,
                "created_at": str(artifact.created_at),
                "updated_at": str(artifact.updated_at),
            },
        )

    def load_latest(
        self,
        production_id: str,
        artifact_key: str,
    ) -> RuntimeArtifactPayload | None:
        artifact = self.repository.load_latest(
            production_id=production_id,
            artifact_key=artifact_key,
        )

        if artifact is None:
            return None

        return RuntimeArtifactPayload(
            production_id=artifact.production_id,
            artifact_key=artifact.artifact_key,
            artifact_version=artifact.artifact_version,
            checksum=artifact.checksum,
            payload=self.serializer.deserialize(artifact.payload_json),
            metadata={
                "artifact_id": artifact.id,
                "created_at": str(artifact.created_at),
                "updated_at": str(artifact.updated_at),
            },
        )

    def load_payload(
        self,
        production_id: str,
        artifact_key: str,
        default: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        artifact = self.load_latest(
            production_id=production_id,
            artifact_key=artifact_key,
        )

        if artifact is None:
            return default or {}

        return artifact.payload

    def exists(self, production_id: str, artifact_key: str) -> bool:
        return self.repository.exists(production_id, artifact_key)

    def list(self, production_id: str) -> list[RuntimeArtifactPayload]:
        rows = self.repository.list_by_production(production_id)

        return [
            RuntimeArtifactPayload(
                production_id=row.production_id,
                artifact_key=row.artifact_key,
                artifact_version=row.artifact_version,
                checksum=row.checksum,
                payload=self.serializer.deserialize(row.payload_json),
                metadata={
                    "artifact_id": row.id,
                    "created_at": str(row.created_at),
                    "updated_at": str(row.updated_at),
                },
            )
            for row in rows
        ]

    def delete_by_key(self, production_id: str, artifact_key: str) -> int:
        return self.repository.delete_by_key(production_id, artifact_key)

    def delete_by_production(self, production_id: str) -> int:
        return self.repository.delete_by_production(production_id)

    def save_editing_execution_planner(
        self,
        production_id: str,
        payload: dict[str, Any],
    ) -> RuntimeArtifactPayload:
        return self.save(production_id, keys.EDITING_EXECUTION_PLANNER, payload)

    def load_editing_execution_planner(self, production_id: str) -> dict[str, Any]:
        return self.load_payload(production_id, keys.EDITING_EXECUTION_PLANNER, {})

    def save_timeline(
        self,
        production_id: str,
        payload: dict[str, Any],
    ) -> RuntimeArtifactPayload:
        return self.save(production_id, keys.TIMELINE, payload)

    def load_timeline(self, production_id: str) -> dict[str, Any]:
        return self.load_payload(production_id, keys.TIMELINE, {})

    def save_execution_graph(
        self,
        production_id: str,
        payload: dict[str, Any],
    ) -> RuntimeArtifactPayload:
        return self.save(production_id, keys.EXECUTION_GRAPH, payload)

    def load_execution_graph(self, production_id: str) -> dict[str, Any]:
        return self.load_payload(production_id, keys.EXECUTION_GRAPH, {})

    def save_optimized_execution_graph(
        self,
        production_id: str,
        payload: dict[str, Any],
    ) -> RuntimeArtifactPayload:
        return self.save(production_id, keys.OPTIMIZED_EXECUTION_GRAPH, payload)

    def load_optimized_execution_graph(self, production_id: str) -> dict[str, Any]:
        return self.load_payload(production_id, keys.OPTIMIZED_EXECUTION_GRAPH, {})

    def save_track_context(
        self,
        production_id: str,
        payload: dict[str, Any],
    ) -> RuntimeArtifactPayload:
        return self.save(production_id, keys.TRACK_CONTEXT, payload)

    def load_track_context(self, production_id: str) -> dict[str, Any]:
        return self.load_payload(production_id, keys.TRACK_CONTEXT, {})

    def save_subtitle_track(
        self,
        production_id: str,
        payload: dict[str, Any],
    ) -> RuntimeArtifactPayload:
        return self.save(production_id, keys.SUBTITLE_TRACK, payload)

    def load_subtitle_track(self, production_id: str) -> dict[str, Any]:
        return self.load_payload(production_id, keys.SUBTITLE_TRACK, {})

    def save_video_track(
        self,
        production_id: str,
        payload: dict[str, Any],
    ) -> RuntimeArtifactPayload:
        return self.save(production_id, keys.VIDEO_TRACK, payload)

    def load_video_track(self, production_id: str) -> dict[str, Any]:
        return self.load_payload(production_id, keys.VIDEO_TRACK, {})

    def save_audio_track(
        self,
        production_id: str,
        payload: dict[str, Any],
    ) -> RuntimeArtifactPayload:
        return self.save(production_id, keys.AUDIO_TRACK, payload)

    def load_audio_track(self, production_id: str) -> dict[str, Any]:
        return self.load_payload(production_id, keys.AUDIO_TRACK, {})

    def save_composition(
        self,
        production_id: str,
        payload: dict[str, Any],
    ) -> RuntimeArtifactPayload:
        return self.save(production_id, keys.COMPOSITION, payload)

    def load_composition(self, production_id: str) -> dict[str, Any]:
        return self.load_payload(production_id, keys.COMPOSITION, {})

    def save_render_instructions(
        self,
        production_id: str,
        payload: dict[str, Any],
    ) -> RuntimeArtifactPayload:
        return self.save(production_id, keys.RENDER_INSTRUCTIONS, payload)

    def load_render_instructions(self, production_id: str) -> dict[str, Any]:
        return self.load_payload(production_id, keys.RENDER_INSTRUCTIONS, {})

    def save_render_plan(
        self,
        production_id: str,
        payload: dict[str, Any],
    ) -> RuntimeArtifactPayload:
        return self.save(production_id, keys.RENDER_PLAN, payload)

    def load_render_plan(self, production_id: str) -> dict[str, Any]:
        return self.load_payload(production_id, keys.RENDER_PLAN, {})

    def save_render_graph(
        self,
        production_id: str,
        payload: dict[str, Any],
    ) -> RuntimeArtifactPayload:
        return self.save(production_id, keys.RENDER_GRAPH, payload)

    def load_render_graph(self, production_id: str) -> dict[str, Any]:
        return self.load_payload(production_id, keys.RENDER_GRAPH, {})

    def save_render_schedule(
        self,
        production_id: str,
        payload: dict[str, Any],
    ) -> RuntimeArtifactPayload:
        return self.save(production_id, keys.RENDER_SCHEDULE, payload)

    def load_render_schedule(self, production_id: str) -> dict[str, Any]:
        return self.load_payload(production_id, keys.RENDER_SCHEDULE, {})

    def save_resolved_assets(
        self,
        production_id: str,
        payload: dict[str, Any],
    ) -> RuntimeArtifactPayload:
        return self.save(production_id, keys.RESOLVED_ASSETS, payload)

    def load_resolved_assets(self, production_id: str) -> dict[str, Any]:
        return self.load_payload(production_id, keys.RESOLVED_ASSETS, {})

    def save_ffmpeg_command_plan(
        self,
        production_id: str,
        payload: dict[str, Any],
    ) -> RuntimeArtifactPayload:
        return self.save(production_id, keys.FFMPEG_COMMAND_PLAN, payload)

    def load_ffmpeg_command_plan(self, production_id: str) -> dict[str, Any]:
        return self.load_payload(production_id, keys.FFMPEG_COMMAND_PLAN, {})