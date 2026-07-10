from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TimelineInput:
    input_id: str
    input_type: str
    local_path: str
    asset_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "input_id": self.input_id,
            "input_type": self.input_type,
            "local_path": self.local_path,
            "asset_id": self.asset_id,
            "metadata": self.metadata,
        }


@dataclass
class TimelineInstruction:
    instruction_id: str
    instruction_type: str
    track_type: str
    start_time: float
    end_time: float
    layer: int
    input_id: str | None = None
    target_id: str | None = None
    parameters: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        return max(0.0, self.end_time - self.start_time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "instruction_id": self.instruction_id,
            "instruction_type": self.instruction_type,
            "track_type": self.track_type,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "layer": self.layer,
            "input_id": self.input_id,
            "target_id": self.target_id,
            "parameters": self.parameters,
            "metadata": self.metadata,
        }


@dataclass
class TimelineCompilerIssue:
    level: str
    code: str
    message: str
    source_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "level": self.level,
            "code": self.code,
            "message": self.message,
            "source_id": self.source_id,
            "metadata": self.metadata,
        }


@dataclass
class ExecutionTimeline:
    production_id: str
    version: str
    duration: float
    width: int
    height: int
    fps: float
    inputs: list[TimelineInput]
    instructions: list[TimelineInstruction]
    issues: list[TimelineCompilerIssue] = field(default_factory=list)
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
            "inputs": [item.to_dict() for item in self.inputs],
            "instructions": [
                item.to_dict()
                for item in self.instructions
            ],
            "issues": [item.to_dict() for item in self.issues],
            "metadata": self.metadata,
        }