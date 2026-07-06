from __future__ import annotations

from typing import Any

from app.render.scheduler.dependency_scheduler import DependencyScheduler
from app.render.scheduler.models import RenderSchedule, ScheduledRenderStep


class RenderScheduleBuilder:
    def __init__(self):
        self.dependency_scheduler = DependencyScheduler()

    def build(
        self,
        production_id: str,
        render_graph: dict[str, Any],
    ) -> RenderSchedule:
        scheduled_nodes = self.dependency_scheduler.schedule(render_graph)

        steps: list[ScheduledRenderStep] = []

        for index, scheduled in enumerate(scheduled_nodes):
            node = scheduled.get("node", {})
            if not isinstance(node, dict):
                continue

            steps.append(
                ScheduledRenderStep(
                    schedule_id=f"schedule_{index}",
                    node_id=str(node.get("node_id") or ""),
                    operation=str(node.get("operation") or ""),
                    order_index=int(scheduled.get("order_index", index)),
                    can_run_parallel=bool(
                        scheduled.get("can_run_parallel", False)
                    ),
                    inputs=node.get("inputs")
                    if isinstance(node.get("inputs"), dict)
                    else {},
                    outputs=node.get("outputs")
                    if isinstance(node.get("outputs"), dict)
                    else {},
                    parameters=node.get("parameters")
                    if isinstance(node.get("parameters"), dict)
                    else {},
                )
            )

        return RenderSchedule(
            production_id=production_id,
            steps=steps,
            metadata={
                "builder": "render_schedule_builder",
                "step_count": len(steps),
                "parallel_step_count": sum(
                    1 for step in steps if step.can_run_parallel
                ),
                "source": "render_graph",
            },
        )