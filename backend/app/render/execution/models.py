from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.render.execution.enums import (
    RenderArtifactType,
    RenderNodeStatus,
    RenderNodeType,
    RenderStage,
)


@dataclass
class RenderConfig:
    width: int = 1080
    height: int = 1920
    fps: float = 30.0

    video_codec: str = "libx264"
    audio_codec: str = "aac"
    pixel_format: str = "yuv420p"

    video_bitrate: str | None = None
    audio_bitrate: str = "192k"
    preset: str = "medium"
    crf: int = 23

    overwrite: bool = True
    generate_thumbnail: bool = True
    generate_report: bool = True

    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "width": self.width,
            "height": self.height,
            "fps": self.fps,
            "video_codec": self.video_codec,
            "audio_codec": self.audio_codec,
            "pixel_format": self.pixel_format,
            "video_bitrate": self.video_bitrate,
            "audio_bitrate": self.audio_bitrate,
            "preset": self.preset,
            "crf": self.crf,
            "overwrite": self.overwrite,
            "generate_thumbnail": self.generate_thumbnail,
            "generate_report": self.generate_report,
            "metadata": self.metadata,
        }


@dataclass
class RenderArtifact:
    artifact_id: str
    artifact_type: RenderArtifactType | str
    local_path: str

    mime_type: str | None = None
    checksum: str | None = None
    size: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        artifact_type = (
            self.artifact_type.value
            if hasattr(self.artifact_type, "value")
            else str(self.artifact_type)
        )

        return {
            "artifact_id": self.artifact_id,
            "artifact_type": artifact_type,
            "local_path": self.local_path,
            "mime_type": self.mime_type,
            "checksum": self.checksum,
            "size": self.size,
            "metadata": self.metadata,
        }


@dataclass
class RenderNode:
    node_id: str
    node_type: RenderNodeType | str
    stage: RenderStage | str

    dependencies: list[str] = field(default_factory=list)
    status: RenderNodeStatus | str = RenderNodeStatus.PENDING

    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)

    priority: int = 100
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self._enum_value(self.node_type),
            "stage": self._enum_value(self.stage),
            "dependencies": list(self.dependencies),
            "status": self._enum_value(self.status),
            "inputs": self.inputs,
            "outputs": self.outputs,
            "priority": self.priority,
            "metadata": self.metadata,
        }

    def _enum_value(self, value: Any) -> str:
        return value.value if hasattr(value, "value") else str(value)


@dataclass
class RenderGraphIssue:
    level: str
    code: str
    message: str
    node_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "level": self.level,
            "code": self.code,
            "message": self.message,
            "node_id": self.node_id,
            "metadata": self.metadata,
        }


@dataclass
class RenderGraph:
    production_id: str
    version: str
    nodes: list[RenderNode]

    issues: list[RenderGraphIssue] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "version": self.version,
            "nodes": [node.to_dict() for node in self.nodes],
            "issues": [issue.to_dict() for issue in self.issues],
            "metadata": self.metadata,
        }


@dataclass
class RenderResult:
    production_id: str
    success: bool
    artifacts: list[RenderArtifact]

    failed_node_id: str | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "success": self.success,
            "artifacts": [
                artifact.to_dict()
                for artifact in self.artifacts
            ],
            "failed_node_id": self.failed_node_id,
            "error": self.error,
            "metadata": self.metadata,
        }

@dataclass
class RenderExecutionNode:
    node_id: str
    node_type: str
    stage: str
    execution_level: int
    execution_index: int
    dependencies: list[str] = field(default_factory=list)
    status: RenderNodeStatus | str = RenderNodeStatus.PENDING
    priority: int = 100
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self._enum_value(self.node_type),
            "stage": self._enum_value(self.stage),
            "execution_level": self.execution_level,
            "execution_index": self.execution_index,
            "dependencies": list(self.dependencies),
            "status": self._enum_value(self.status),
            "priority": self.priority,
            "metadata": self.metadata,
        }

    def _enum_value(self, value: Any) -> str:
        return value.value if hasattr(value, "value") else str(value)


@dataclass
class RenderExecutionPlan:
    production_id: str
    version: str
    nodes: list[RenderExecutionNode]
    execution_order: list[str]
    levels: list[list[str]]
    issues: list[RenderGraphIssue] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "version": self.version,
            "nodes": [node.to_dict() for node in self.nodes],
            "execution_order": list(self.execution_order),
            "levels": [list(level) for level in self.levels],
            "issues": [issue.to_dict() for issue in self.issues],
            "metadata": self.metadata,
        }

@dataclass
class RenderNodeExecutionResult:
    node_id: str
    status: RenderNodeStatus | str
    started_at: str
    finished_at: str
    duration_seconds: float

    outputs: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "status": self._enum_value(self.status),
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_seconds": self.duration_seconds,
            "outputs": self.outputs,
            "error": self.error,
            "metadata": self.metadata,
        }

    def _enum_value(self, value: Any) -> str:
        return value.value if hasattr(value, "value") else str(value)


@dataclass
class RenderExecutionEvent:
    event_type: str
    timestamp: str
    node_id: str | None = None
    message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "node_id": self.node_id,
            "message": self.message,
            "metadata": self.metadata,
        }


@dataclass
class RenderExecutionSummary:
    production_id: str
    success: bool

    node_results: list[RenderNodeExecutionResult]
    events: list[RenderExecutionEvent]

    completed_node_count: int
    failed_node_count: int
    skipped_node_count: int

    progress: float
    duration_seconds: float

    failed_node_id: str | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "success": self.success,
            "node_results": [
                item.to_dict()
                for item in self.node_results
            ],
            "events": [
                item.to_dict()
                for item in self.events
            ],
            "completed_node_count": self.completed_node_count,
            "failed_node_count": self.failed_node_count,
            "skipped_node_count": self.skipped_node_count,
            "progress": self.progress,
            "duration_seconds": self.duration_seconds,
            "failed_node_id": self.failed_node_id,
            "error": self.error,
            "metadata": self.metadata,
        }    
