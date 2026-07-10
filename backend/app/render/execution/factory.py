from __future__ import annotations

from app.render.execution.executor_runtime import (
    RenderExecutionRuntime,
)
from app.render.execution.executors import (
    ArtifactExecutor,
    AudioMixExecutor,
    ComposeVideoExecutor,
    DecodeExecutor,
    EffectExecutor,
    EncodeExecutor,
    OverlayExecutor,
    PrepareInputsNodeExecutor,
    SubtitleExecutor,
)
from app.render.execution.registry import (
    RenderNodeExecutorRegistry,
)
from app.render.execution.runtime import (
    RenderArchitectureRuntime,
)
from app.render.execution.scheduler_runtime import (
    RenderSchedulerRuntime,
)


def build_render_architecture_runtime() -> (
    RenderArchitectureRuntime
):
    return RenderArchitectureRuntime()


def build_render_scheduler_runtime() -> (
    RenderSchedulerRuntime
):
    return RenderSchedulerRuntime()


def build_default_render_node_executor_registry(
    delay_seconds: float = 0.01,
    fail_node_ids: set[str] | None = None,
) -> RenderNodeExecutorRegistry:
    options = {
        "delay_seconds": delay_seconds,
        "fail_node_ids": fail_node_ids or set(),
    }

    return RenderNodeExecutorRegistry(
        executors=[
            PrepareInputsNodeExecutor(),
            DecodeExecutor(**options),
            ComposeVideoExecutor(**options),
            OverlayExecutor(**options),
            EffectExecutor(**options),
            SubtitleExecutor(**options),
            AudioMixExecutor(**options),
            EncodeExecutor(**options),
            ArtifactExecutor(**options),
        ]
    )


def build_render_execution_runtime(
    delay_seconds: float = 0.01,
    fail_node_ids: set[str] | None = None,
) -> RenderExecutionRuntime:
    return RenderExecutionRuntime(
        registry=(
            build_default_render_node_executor_registry(
                delay_seconds=delay_seconds,
                fail_node_ids=fail_node_ids,
            )
        )
    )