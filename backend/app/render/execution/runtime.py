from __future__ import annotations

from pathlib import Path

from app.render.execution.context import RenderContext
from app.render.execution.graph import RenderGraphBuilder
from app.render.execution.models import RenderConfig
from app.render.execution.validator import (
    RenderGraphValidator,
)
from app.timeline.compiler.models import ExecutionTimeline


class RenderArchitectureRuntime:
    def __init__(
        self,
        graph_builder: RenderGraphBuilder | None = None,
        graph_validator: RenderGraphValidator | None = None,
    ):
        self.graph_builder = (
            graph_builder or RenderGraphBuilder()
        )
        self.graph_validator = (
            graph_validator or RenderGraphValidator()
        )

    def build_context(
        self,
        execution_timeline: ExecutionTimeline,
        storage_root: str = "storage/render",
        render_config: RenderConfig | None = None,
    ) -> RenderContext:
        production_root = (
            Path(storage_root)
            / execution_timeline.production_id
        )

        context = RenderContext(
            production_id=(
                execution_timeline.production_id
            ),
            execution_timeline=execution_timeline,
            working_directory=str(
                production_root / "working"
            ),
            temp_directory=str(
                production_root / "temp"
            ),
            output_directory=str(
                production_root / "output"
            ),
            artifact_directory=str(
                production_root / "artifacts"
            ),
            render_config=(
                render_config or RenderConfig(
                    width=execution_timeline.width,
                    height=execution_timeline.height,
                    fps=execution_timeline.fps,
                )
            ),
            metadata={
                "runtime": "RenderArchitectureRuntime",
                "execution_timeline_version": (
                    execution_timeline.version
                ),
            },
        )

        context.ensure_directories()

        graph = self.graph_builder.build(context)
        context.graph = self.graph_validator.validate(
            graph
        )

        return context