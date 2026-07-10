from __future__ import annotations

import time
from datetime import datetime, timezone

from app.render.execution.context import RenderContext
from app.render.execution.enums import RenderNodeStatus
from app.render.execution.models import (
    RenderExecutionEvent,
    RenderExecutionPlan,
    RenderExecutionSummary,
    RenderNode,
    RenderNodeExecutionResult,
)
from app.render.execution.registry import (
    RenderNodeExecutorRegistry,
)
from app.render.execution.scheduler import (
    RenderGraphScheduler,
)


class RenderExecutionRuntime:
    def __init__(
        self,
        registry: RenderNodeExecutorRegistry,
        scheduler: RenderGraphScheduler | None = None,
    ):
        self.registry = registry
        self.scheduler = scheduler or RenderGraphScheduler()

    def run(
        self,
        context: RenderContext,
        plan: RenderExecutionPlan,
    ) -> RenderExecutionSummary:
        started_counter = time.perf_counter()

        events: list[RenderExecutionEvent] = []
        node_results: list[RenderNodeExecutionResult] = []

        self._add_event(
            events=events,
            event_type="START",
            message="Render execution started.",
        )

        context.runtime_state.progress = 0.0
        context.runtime_state.completed_node_ids = []
        context.runtime_state.failed_node_ids = []

        graph_node_map = self._graph_node_map(context)

        while True:
            ready_nodes = self.scheduler.ready_nodes(plan)

            if not ready_nodes:
                break

            ready_nodes.sort(
                key=lambda item: (
                    item.execution_level,
                    item.priority,
                    item.execution_index,
                    item.node_id,
                )
            )

            for execution_node in ready_nodes:
                graph_node = graph_node_map.get(
                    execution_node.node_id
                )

                if graph_node is None:
                    raise RuntimeError(
                        "Execution-plan node does not exist "
                        f"in render graph: {execution_node.node_id}"
                    )

                context.runtime_state.current_node_id = (
                    execution_node.node_id
                )

                self.scheduler.mark_running(
                    plan=plan,
                    node_id=execution_node.node_id,
                )

                self._add_event(
                    events=events,
                    event_type="NODE_STARTED",
                    node_id=execution_node.node_id,
                    message=(
                        f"Node started: "
                        f"{execution_node.node_id}"
                    ),
                )

                result = self._execute_node_safely(
                    context=context,
                    node=graph_node,
                )

                node_results.append(result)

                if self._status_value(result.status) == (
                    RenderNodeStatus.COMPLETED.value
                ):
                    self.scheduler.mark_completed(
                        plan=plan,
                        node_id=execution_node.node_id,
                    )

                    context.runtime_state.completed_node_ids.append(
                        execution_node.node_id
                    )

                    self._add_event(
                        events=events,
                        event_type="NODE_COMPLETED",
                        node_id=execution_node.node_id,
                        message=(
                            f"Node completed: "
                            f"{execution_node.node_id}"
                        ),
                        metadata={
                            "duration_seconds": (
                                result.duration_seconds
                            ),
                        },
                    )
                else:
                    self.scheduler.mark_failed(
                        plan=plan,
                        node_id=execution_node.node_id,
                        error=result.error,
                    )

                    context.runtime_state.failed_node_ids.append(
                        execution_node.node_id
                    )

                    self._add_event(
                        events=events,
                        event_type="NODE_FAILED",
                        node_id=execution_node.node_id,
                        message=(
                            result.error
                            or "Render node failed."
                        ),
                    )

                self._update_progress(
                    context=context,
                    plan=plan,
                )

        context.runtime_state.current_node_id = None

        counts = self._status_counts(plan)

        success = (
            counts["failed"] == 0
            and counts["skipped"] == 0
            and counts["completed"] == len(plan.nodes)
        )

        final_event_type = (
            "FINISHED"
            if success
            else "FAILED"
        )

        self._add_event(
            events=events,
            event_type=final_event_type,
            message=(
                "Render execution completed."
                if success
                else "Render execution failed."
            ),
        )

        duration_seconds = round(
            time.perf_counter() - started_counter,
            6,
        )

        failed_result = next(
            (
                item
                for item in node_results
                if self._status_value(item.status)
                == RenderNodeStatus.FAILED.value
            ),
            None,
        )

        context.runtime_state.progress = (
            100.0
            if success
            else context.runtime_state.progress
        )

        context.runtime_state.metadata = {
            **context.runtime_state.metadata,
            "execution_success": success,
            "completed_node_count": counts["completed"],
            "failed_node_count": counts["failed"],
            "skipped_node_count": counts["skipped"],
            "event_count": len(events),
            "execution_duration_seconds": duration_seconds,
        }

        return RenderExecutionSummary(
            production_id=context.production_id,
            success=success,
            node_results=node_results,
            events=events,
            completed_node_count=counts["completed"],
            failed_node_count=counts["failed"],
            skipped_node_count=counts["skipped"],
            progress=round(
                context.runtime_state.progress,
                2,
            ),
            duration_seconds=duration_seconds,
            failed_node_id=(
                failed_result.node_id
                if failed_result
                else None
            ),
            error=(
                failed_result.error
                if failed_result
                else None
            ),
            metadata={
                "runtime": "RenderExecutionRuntime",
                "registry_executor_count": (
                    self.registry.count()
                ),
                "execution_plan_version": plan.version,
            },
        )

    def _execute_node_safely(
        self,
        context: RenderContext,
        node: RenderNode,
    ) -> RenderNodeExecutionResult:
        try:
            return self.registry.execute_node(
                context=context,
                node=node,
            )
        except Exception as error:
            now = self._now()

            return RenderNodeExecutionResult(
                node_id=node.node_id,
                status=RenderNodeStatus.FAILED,
                started_at=now,
                finished_at=now,
                duration_seconds=0.0,
                outputs={},
                error=str(error),
                metadata={
                    "executor": None,
                    "registry_failure": True,
                },
            )

    def _graph_node_map(
        self,
        context: RenderContext,
    ) -> dict[str, RenderNode]:
        if context.graph is None:
            raise RuntimeError(
                "Render context has no graph."
            )

        return {
            node.node_id: node
            for node in context.graph.nodes
        }

    def _update_progress(
        self,
        context: RenderContext,
        plan: RenderExecutionPlan,
    ) -> None:
        terminal_statuses = {
            RenderNodeStatus.COMPLETED.value,
            RenderNodeStatus.FAILED.value,
            RenderNodeStatus.SKIPPED.value,
        }

        terminal_count = sum(
            1
            for node in plan.nodes
            if self._status_value(node.status)
            in terminal_statuses
        )

        total = max(1, len(plan.nodes))

        context.runtime_state.progress = round(
            terminal_count / total * 100.0,
            2,
        )

    def _status_counts(
        self,
        plan: RenderExecutionPlan,
    ) -> dict[str, int]:
        counts = {
            "completed": 0,
            "failed": 0,
            "skipped": 0,
            "pending": 0,
            "ready": 0,
            "running": 0,
        }

        for node in plan.nodes:
            value = self._status_value(node.status)

            if value in counts:
                counts[value] += 1

        return counts

    def _add_event(
        self,
        events: list[RenderExecutionEvent],
        event_type: str,
        node_id: str | None = None,
        message: str | None = None,
        metadata: dict | None = None,
    ) -> None:
        events.append(
            RenderExecutionEvent(
                event_type=event_type,
                timestamp=self._now(),
                node_id=node_id,
                message=message,
                metadata=metadata or {},
            )
        )

    def _status_value(self, status) -> str:
        return (
            status.value
            if hasattr(status, "value")
            else str(status)
        )

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()