from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FFmpegCommand:
    command_id: str
    args: list[str] = field(default_factory=list)
    command_preview: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "command_id": self.command_id,
            "args": self.args,
            "command_preview": self.command_preview,
            "metadata": self.metadata,
        }


@dataclass
class FFmpegCommandPlan:
    production_id: str
    commands: list[FFmpegCommand] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "commands": [command.to_dict() for command in self.commands],
            "metadata": self.metadata,
        }