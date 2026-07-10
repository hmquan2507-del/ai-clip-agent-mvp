from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.render.ffmpeg.instructions.enums import (
    FFmpegInstructionStatus,
    FFmpegInstructionType,
    FFmpegStreamType,
)


@dataclass
class FFmpegInputSpec:
    input_id: str
    prepared_path: str
    input_type: str
    ffmpeg_input_index: int

    asset_id: str | None = None
    duration: float | None = None
    has_video: bool = False
    has_audio: bool = False

    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "input_id": self.input_id,
            "prepared_path": self.prepared_path,
            "input_type": self.input_type,
            "ffmpeg_input_index": self.ffmpeg_input_index,
            "asset_id": self.asset_id,
            "duration": self.duration,
            "has_video": self.has_video,
            "has_audio": self.has_audio,
            "metadata": self.metadata,
        }


@dataclass
class FFmpegRenderInstruction:
    instruction_id: str
    instruction_type: FFmpegInstructionType | str
    stream_type: FFmpegStreamType | str

    start_time: float
    end_time: float

    source_input_id: str | None = None
    source_stream_label: str | None = None
    output_stream_label: str | None = None
    target_id: str | None = None

    layer: int = 1
    order: int = 0

    parameters: dict[str, Any] = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)

    status: FFmpegInstructionStatus | str = (
        FFmpegInstructionStatus.PENDING
    )

    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        return max(0.0, self.end_time - self.start_time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "instruction_id": self.instruction_id,
            "instruction_type": self._value(
                self.instruction_type
            ),
            "stream_type": self._value(
                self.stream_type
            ),
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "source_input_id": self.source_input_id,
            "source_stream_label": self.source_stream_label,
            "output_stream_label": self.output_stream_label,
            "target_id": self.target_id,
            "layer": self.layer,
            "order": self.order,
            "parameters": self.parameters,
            "dependencies": list(self.dependencies),
            "status": self._value(self.status),
            "metadata": self.metadata,
        }

    def _value(self, value: Any) -> str:
        return (
            value.value
            if hasattr(value, "value")
            else str(value)
        )


@dataclass
class FFmpegInstructionIssue:
    level: str
    code: str
    message: str

    instruction_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "level": self.level,
            "code": self.code,
            "message": self.message,
            "instruction_id": self.instruction_id,
            "metadata": self.metadata,
        }


@dataclass
class FFmpegInstructionPlan:
    production_id: str
    version: str

    duration: float
    width: int
    height: int
    fps: float

    inputs: list[FFmpegInputSpec]
    instructions: list[FFmpegRenderInstruction]
    issues: list[FFmpegInstructionIssue]

    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "version": self.version,
            "duration": self.duration,
            "canvas": {
                "width": self.width,
                "height": self.height,
                "fps": self.fps,
            },
            "inputs": [
                item.to_dict()
                for item in self.inputs
            ],
            "instructions": [
                item.to_dict()
                for item in self.instructions
            ],
            "issues": [
                item.to_dict()
                for item in self.issues
            ],
            "metadata": self.metadata,
        }