from __future__ import annotations

from app.render.execution.context import RenderContext
from app.render.execution.models import (
    RenderExecutionPlan,
)
from app.render.execution.scheduler import (
    RenderGraphScheduler,
)


class RenderSchedulerRuntime:
    def __init__(
        self,
        scheduler: RenderGraphScheduler | None = None,
    ):
        self.scheduler = (
            scheduler or RenderGraphScheduler()
        )

    def schedule(
        self,
        context: RenderContext,
    ) -> RenderExecutionPlan:
        if context.graph is None:
            raise RuntimeError(
                "Render context has no graph."
            )

        plan = self.scheduler.schedule(
            context.graph
        )

        context.metadata = {
            **context.metadata,
            "execution_plan_version": plan.version,
            "execution_plan_node_count": len(
                plan.nodes
            ),
            "execution_level_count": len(
                plan.levels
            ),
            "scheduler_ready": plan.metadata.get(
                "scheduled",
                False,
            ),
        }

        context.runtime_state.metadata = {
            **context.runtime_state.metadata,
            "execution_plan": plan.to_dict(),
        }

        return plan