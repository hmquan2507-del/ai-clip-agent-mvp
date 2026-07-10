from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from app.render.execution.context import RenderContext
from app.render.execution.preloader import (
    RenderAssetPreloadResult,
    RenderAssetPreloader,
)
from app.render.ffmpeg.execution.command_builder import (
    FFmpegCommandBuilder,
)
from app.render.ffmpeg.execution.executor import (
    FFmpegCommandExecutor,
)
from app.render.ffmpeg.execution.models import (
    FFmpegExecutionResult,
    FFmpegProgressEvent,
)
from app.render.ffmpeg.filtergraph import (
    FFmpegFilterGraph,
    FFmpegFilterGraphBuilder,
    FFmpegFilterGraphValidator,
)
from app.render.ffmpeg.instructions import (
    FFmpegInstructionCompiler,
    FFmpegInstructionPlan,
    FFmpegInstructionPlanValidator,
)


ProgressCallback = Callable[
    [FFmpegProgressEvent],
    None,
]


@dataclass
class FFmpegRenderPipelineResult:
    preload_result: RenderAssetPreloadResult
    instruction_plan: FFmpegInstructionPlan
    filter_graph: FFmpegFilterGraph
    execution_result: FFmpegExecutionResult
    metadata: dict[str, Any] = field(default_factory=dict)


class FFmpegRenderPipeline:
    def __init__(
        self,
        preloader: RenderAssetPreloader | None = None,
        instruction_compiler: (
            FFmpegInstructionCompiler | None
        ) = None,
        instruction_validator: (
            FFmpegInstructionPlanValidator | None
        ) = None,
        filtergraph_builder: (
            FFmpegFilterGraphBuilder | None
        ) = None,
        filtergraph_validator: (
            FFmpegFilterGraphValidator | None
        ) = None,
        command_builder: FFmpegCommandBuilder | None = None,
        command_executor: FFmpegCommandExecutor | None = None,
    ):
        self.preloader = (
            preloader or RenderAssetPreloader()
        )
        self.instruction_compiler = (
            instruction_compiler
            or FFmpegInstructionCompiler()
        )
        self.instruction_validator = (
            instruction_validator
            or FFmpegInstructionPlanValidator()
        )
        self.filtergraph_builder = (
            filtergraph_builder
            or FFmpegFilterGraphBuilder()
        )
        self.filtergraph_validator = (
            filtergraph_validator
            or FFmpegFilterGraphValidator()
        )
        self.command_builder = (
            command_builder
            or FFmpegCommandBuilder()
        )
        self.command_executor = (
            command_executor
            or FFmpegCommandExecutor()
        )

    def render(
        self,
        context: RenderContext,
        progress_callback: ProgressCallback | None = None,
    ) -> FFmpegRenderPipelineResult:
        preload_result = self.preloader.preload(
            context
        )

        if not preload_result.success:
            raise RuntimeError(
                "Render asset preload failed."
            )

        instruction_plan = (
            self.instruction_compiler.compile(
                context=context,
                preload_result=preload_result,
            )
        )

        instruction_plan = (
            self.instruction_validator.validate(
                instruction_plan
            )
        )

        if not instruction_plan.metadata.get(
            "valid",
            False,
        ):
            raise RuntimeError(
                "FFmpeg instruction plan is invalid."
            )

        filter_graph = (
            self.filtergraph_builder.build(
                instruction_plan
            )
        )

        filter_graph = (
            self.filtergraph_validator
            .validate_contract(
                filter_graph
            )
        )

        if not filter_graph.metadata.get(
            "contract_valid",
            False,
        ):
            raise RuntimeError(
                "FFmpeg filter graph contract is invalid."
            )

        command = self.command_builder.build(
            graph=filter_graph,
            enable_progress=True,
            log_level="error",
        )

        execution_result = (
            self.command_executor.execute(
                production_id=(
                    context.production_id
                ),
                command=command,
                progress_callback=(
                    progress_callback
                ),
            )
        )

        return FFmpegRenderPipelineResult(
            preload_result=preload_result,
            instruction_plan=instruction_plan,
            filter_graph=filter_graph,
            execution_result=execution_result,
            metadata={
                "runtime": "FFmpegRenderPipeline",
                "render_success": (
                    execution_result.success
                ),
            },
        )