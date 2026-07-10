from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.render.execution.models import (
    RenderArtifact,
    RenderConfig,
    RenderGraph,
)
from app.timeline.compiler.models import ExecutionTimeline


@dataclass
class RenderRuntimeState:
    current_node_id: str | None = None
    completed_node_ids: list[str] = field(default_factory=list)
    failed_node_ids: list[str] = field(default_factory=list)
    progress: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "current_node_id": self.current_node_id,
            "completed_node_ids": self.completed_node_ids,
            "failed_node_ids": self.failed_node_ids,
            "progress": self.progress,
            "metadata": self.metadata,
        }


@dataclass
class RenderContext:
    production_id: str
    execution_timeline: ExecutionTimeline

    working_directory: str
    temp_directory: str
    output_directory: str
    artifact_directory: str

    render_config: RenderConfig = field(
        default_factory=RenderConfig
    )

    graph: RenderGraph | None = None
    artifacts: list[RenderArtifact] = field(default_factory=list)
    runtime_state: RenderRuntimeState = field(
        default_factory=RenderRuntimeState
    )

    metadata: dict[str, Any] = field(default_factory=dict)

    def ensure_directories(self) -> None:
        for value in {
            self.working_directory,
            self.temp_directory,
            self.output_directory,
            self.artifact_directory,
        }:
            Path(value).mkdir(
                parents=True,
                exist_ok=True,
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "execution_timeline": (
                self.execution_timeline.to_dict()
            ),
            "working_directory": self.working_directory,
            "temp_directory": self.temp_directory,
            "output_directory": self.output_directory,
            "artifact_directory": self.artifact_directory,
            "render_config": self.render_config.to_dict(),
            "graph": (
                self.graph.to_dict()
                if self.graph is not None
                else None
            ),
            "artifacts": [
                artifact.to_dict()
                for artifact in self.artifacts
            ],
            "runtime_state": self.runtime_state.to_dict(),
            "metadata": self.metadata,
        }