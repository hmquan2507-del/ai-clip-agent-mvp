from __future__ import annotations

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