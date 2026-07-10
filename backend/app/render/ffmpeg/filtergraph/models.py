from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FFmpegInputArgument:
    input_id: str
    input_index: int
    prepared_path: str
    arguments: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "input_id": self.input_id,
            "input_index": self.input_index,
            "prepared_path": self.prepared_path,
            "arguments": list(self.arguments),
            "metadata": self.metadata,
        }


@dataclass
class FFmpegFilterChain:
    chain_id: str
    filter_text: str
    input_labels: list[str]
    output_label: str | None
    stage: str
    order: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "chain_id": self.chain_id,
            "filter_text": self.filter_text,
            "input_labels": list(self.input_labels),
            "output_label": self.output_label,
            "stage": self.stage,
            "order": self.order,
            "metadata": self.metadata,
        }


@dataclass
class FFmpegFilterGraphIssue:
    level: str
    code: str
    message: str
    chain_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "level": self.level,
            "code": self.code,
            "message": self.message,
            "chain_id": self.chain_id,
            "metadata": self.metadata,
        }


@dataclass
class FFmpegFilterGraph:
    production_id: str
    version: str

    input_arguments: list[FFmpegInputArgument]
    chains: list[FFmpegFilterChain]

    filter_complex: str
    video_output_label: str | None
    audio_output_label: str | None

    map_arguments: list[str]
    output_arguments: list[str]
    output_path: str

    issues: list[FFmpegFilterGraphIssue] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def build_command(
        self,
        ffmpeg_binary: str = "ffmpeg",
    ) -> list[str]:
        command = [ffmpeg_binary, "-y"]

        for item in sorted(
            self.input_arguments,
            key=lambda value: value.input_index,
        ):
            command.extend(item.arguments)

        if self.filter_complex:
            command.extend(
                [
                    "-filter_complex",
                    self.filter_complex,
                ]
            )

        command.extend(self.map_arguments)
        command.extend(self.output_arguments)
        command.append(self.output_path)

        return command

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "version": self.version,
            "input_arguments": [
                item.to_dict()
                for item in self.input_arguments
            ],
            "chains": [
                item.to_dict()
                for item in self.chains
            ],
            "filter_complex": self.filter_complex,
            "video_output_label": self.video_output_label,
            "audio_output_label": self.audio_output_label,
            "map_arguments": list(self.map_arguments),
            "output_arguments": list(self.output_arguments),
            "output_path": self.output_path,
            "issues": [
                item.to_dict()
                for item in self.issues
            ],
            "metadata": self.metadata,
            "command_preview": self.build_command(),
        }