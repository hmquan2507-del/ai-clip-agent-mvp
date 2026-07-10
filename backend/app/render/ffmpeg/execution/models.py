from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FFmpegCommand:
    binary: str
    arguments: list[str]
    output_path: str
    duration: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_list(self) -> list[str]:
        return [
            self.binary,
            *self.arguments,
        ]

    def to_dict(self) -> dict[str, Any]:
        return {
            "binary": self.binary,
            "arguments": list(self.arguments),
            "command": self.as_list(),
            "output_path": self.output_path,
            "duration": self.duration,
            "metadata": self.metadata,
        }


@dataclass
class FFmpegProgressEvent:
    progress: float
    out_time_seconds: float
    speed: str | None = None
    frame: int | None = None
    fps: float | None = None
    bitrate: str | None = None
    total_size: int | None = None
    status: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "progress": self.progress,
            "out_time_seconds": self.out_time_seconds,
            "speed": self.speed,
            "frame": self.frame,
            "fps": self.fps,
            "bitrate": self.bitrate,
            "total_size": self.total_size,
            "status": self.status,
            "metadata": self.metadata,
        }


@dataclass
class FFmpegExecutionIssue:
    level: str
    code: str
    message: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "level": self.level,
            "code": self.code,
            "message": self.message,
            "metadata": self.metadata,
        }


@dataclass
class FFmpegExecutionResult:
    production_id: str
    success: bool
    returncode: int | None

    output_path: str
    command: FFmpegCommand

    started_at: str
    finished_at: str
    duration_seconds: float

    progress_events: list[FFmpegProgressEvent]
    issues: list[FFmpegExecutionIssue]

    stderr_tail: str | None = None

    output_file_size: int | None = None
    output_duration: float | None = None
    output_width: int | None = None
    output_height: int | None = None
    output_fps: float | None = None
    output_video_codec: str | None = None
    output_audio_codec: str | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "success": self.success,
            "returncode": self.returncode,
            "output_path": self.output_path,
            "command": self.command.to_dict(),
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_seconds": self.duration_seconds,
            "progress_events": [
                item.to_dict()
                for item in self.progress_events
            ],
            "issues": [
                issue.to_dict()
                for issue in self.issues
            ],
            "stderr_tail": self.stderr_tail,
            "output_file_size": self.output_file_size,
            "output_duration": self.output_duration,
            "output_width": self.output_width,
            "output_height": self.output_height,
            "output_fps": self.output_fps,
            "output_video_codec": self.output_video_codec,
            "output_audio_codec": self.output_audio_codec,
            "metadata": self.metadata,
        }