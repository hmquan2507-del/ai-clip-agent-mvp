from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class StoredRenderArtifact:
    artifact_id: str
    artifact_type: str
    local_path: str

    mime_type: str | None = None
    checksum: str | None = None
    file_size: int | None = None

    duration: float | None = None
    width: int | None = None
    height: int | None = None
    fps: float | None = None

    video_codec: str | None = None
    audio_codec: str | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type,
            "local_path": self.local_path,
            "mime_type": self.mime_type,
            "checksum": self.checksum,
            "file_size": self.file_size,
            "duration": self.duration,
            "width": self.width,
            "height": self.height,
            "fps": self.fps,
            "video_codec": self.video_codec,
            "audio_codec": self.audio_codec,
            "metadata": self.metadata,
        }


@dataclass
class RenderArtifactStoreIssue:
    level: str
    code: str
    message: str
    artifact_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "level": self.level,
            "code": self.code,
            "message": self.message,
            "artifact_id": self.artifact_id,
            "metadata": self.metadata,
        }


@dataclass
class RenderArtifactStoreResult:
    production_id: str
    success: bool

    artifacts: list[StoredRenderArtifact]
    issues: list[RenderArtifactStoreIssue]

    manifest_path: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "success": self.success,
            "artifacts": [
                artifact.to_dict()
                for artifact in self.artifacts
            ],
            "issues": [
                issue.to_dict()
                for issue in self.issues
            ],
            "manifest_path": self.manifest_path,
            "metadata": self.metadata,
        }