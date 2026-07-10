from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PreparedRenderInput:
    input_id: str
    input_type: str
    source_path: str
    prepared_path: str

    asset_id: str | None = None
    checksum: str | None = None
    file_size: int | None = None

    duration: float | None = None
    width: int | None = None
    height: int | None = None
    fps: float | None = None
    video_codec: str | None = None
    audio_codec: str | None = None
    has_video: bool = False
    has_audio: bool = False

    copied: bool = False
    linked: bool = False
    reused: bool = False

    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "input_id": self.input_id,
            "input_type": self.input_type,
            "source_path": self.source_path,
            "prepared_path": self.prepared_path,
            "asset_id": self.asset_id,
            "checksum": self.checksum,
            "file_size": self.file_size,
            "duration": self.duration,
            "width": self.width,
            "height": self.height,
            "fps": self.fps,
            "video_codec": self.video_codec,
            "audio_codec": self.audio_codec,
            "has_video": self.has_video,
            "has_audio": self.has_audio,
            "copied": self.copied,
            "linked": self.linked,
            "reused": self.reused,
            "metadata": self.metadata,
        }


@dataclass
class RenderAssetPreloadIssue:
    level: str
    code: str
    message: str
    input_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "level": self.level,
            "code": self.code,
            "message": self.message,
            "input_id": self.input_id,
            "metadata": self.metadata,
        }


@dataclass
class RenderAssetPreloadResult:
    production_id: str
    prepared_inputs: list[PreparedRenderInput]
    issues: list[RenderAssetPreloadIssue]
    manifest_path: str
    success: bool
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "prepared_inputs": [
                item.to_dict()
                for item in self.prepared_inputs
            ],
            "issues": [
                issue.to_dict()
                for issue in self.issues
            ],
            "manifest_path": self.manifest_path,
            "success": self.success,
            "metadata": self.metadata,
        }