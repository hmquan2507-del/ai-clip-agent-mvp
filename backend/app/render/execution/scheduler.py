from __future__ import annotations

from collections import defaultdict
from heapq import heappop, heappush

from app.render.execution.enums import RenderNodeStatus
from app.render.execution.interfaces import BaseRenderScheduler
from app.render.execution.models import (
    RenderExecutionNode,
    RenderExecutionPlan,
    RenderGraph,
    RenderGraphIssue,
    RenderNode,
)


class RenderGraphScheduler(BaseRenderScheduler):
    def schedule(
        self,
        graph: RenderGraph,
    ) -> RenderExecutionPlan:
        issues = list(graph.issues)

        if any(issue.level == "error" for issue in issues):
            return RenderExecutionPlan(
                production_id=graph.production_id,
                version="15.1.0",
                nodes=[],
                execution_order=[],
                levels=[],
                issues=issues,
                metadata={
                    "scheduler": "RenderGraphScheduler",
                    "scheduled": False,
                    "reason": "graph_has_errors",
                },
            )

        node_map = {
            node.node_id: node
            for node in graph.nodes
        }

        indegree = {
            node.node_id: len(node.dependencies)
            for node in graph.nodes
        }

        dependents: dict[str, list[str]] = defaultdict(list)

        for node in graph.nodes:
            for dependency in node.dependencies:
                dependents[dependency].append(node.node_id)

        ready_heap: list[tuple[int, str]] = []

        for node in graph.nodes:
            if indegree[node.node_id] == 0:
                heappush(
                    ready_heap,
                    (
                        node.priority,
                        node.node_id,
                    ),
                )

        execution_order: list[str] = []
        levels: list[list[str]] = []
        node_levels: dict[str, int] = {}

        while ready_heap:
            current_level_items = []

            while ready_heap:
                current_level_items.append(
                    heappop(ready_heap)
                )

            current_level_items.sort(
                key=lambda item: (
                    item[0],
                    item[1],
                )
            )

            current_level_node_ids = [
                node_id
                for _, node_id in current_level_items
            ]

            level_index = len(levels)
            levels.append(current_level_node_ids)

            next_ready: list[tuple[int, str]] = []

            for _, node_id in current_level_items:
                execution_order.append(node_id)
                node_levels[node_id] = level_index

                for dependent_id in sorted(
                    dependents.get(node_id, [])
                ):
                    indegree[dependent_id] -= 1

                    if indegree[dependent_id] == 0:
                        dependent = node_map[dependent_id]

                        heappush(
                            next_ready,
                            (
                                dependent.priority,
                                dependent.node_id,
                            ),
                        )

            ready_heap = next_ready

        if len(execution_order) != len(graph.nodes):
            issues.append(
                RenderGraphIssue(
                    level="error",
                    code="scheduler_incomplete",
                    message=(
                        "Scheduler could not include every "
                        "render graph node."
                    ),
                    metadata={
                        "graph_node_count": len(graph.nodes),
                        "scheduled_node_count": len(
                            execution_order
                        ),
                    },
                )
            )

        execution_nodes = self._build_execution_nodes(
            graph=graph,
            execution_order=execution_order,
            node_levels=node_levels,
        )

        first_level = (
            set(levels[0])
            if levels
            else set()
        )

        for execution_node in execution_nodes:
            if execution_node.node_id in first_level:
                execution_node.status = (
                    RenderNodeStatus.READY
                )
            else:
                execution_node.status = (
                    RenderNodeStatus.PENDING
                )

        return RenderExecutionPlan(
            production_id=graph.production_id,
            version="15.1.0",
            nodes=execution_nodes,
            execution_order=execution_order,
            levels=levels,
            issues=issues,
            metadata={
                "scheduler": "RenderGraphScheduler",
                "scheduled": not any(
                    issue.level == "error"
                    for issue in issues
                ),
                "node_count": len(graph.nodes),
                "scheduled_node_count": len(
                    execution_order
                ),
                "execution_level_count": len(levels),
                "parallel_group_count": sum(
                    1
                    for level in levels
                    if len(level) > 1
                ),
                "initial_ready_node_count": len(
                    first_level
                ),
            },
        )

    def ready_nodes(
        self,
        plan: RenderExecutionPlan,
    ) -> list[RenderExecutionNode]:
        return [
            node
            for node in plan.nodes
            if self._status_value(node.status)
            == RenderNodeStatus.READY.value
        ]

    def mark_running(
        self,
        plan: RenderExecutionPlan,
        node_id: str,
    ) -> RenderExecutionPlan:
        node = self._require_node(
            plan=plan,
            node_id=node_id,
        )

        if self._status_value(node.status) != (
            RenderNodeStatus.READY.value
        ):
            raise ValueError(
                f"Render node is not ready: {node_id}"
            )

        node.status = RenderNodeStatus.RUNNING

        return plan

    def mark_completed(
        self,
        plan: RenderExecutionPlan,
        node_id: str,
    ) -> RenderExecutionPlan:
        node = self._require_node(
            plan=plan,
            node_id=node_id,
        )

        node.status = RenderNodeStatus.COMPLETED

        self._refresh_ready_nodes(plan)

        return plan

    def mark_failed(
        self,
        plan: RenderExecutionPlan,
        node_id: str,
        error: str | None = None,
    ) -> RenderExecutionPlan:
        node = self._require_node(
            plan=plan,
            node_id=node_id,
        )

        node.status = RenderNodeStatus.FAILED
        node.metadata = {
            **node.metadata,
            "error": error,
        }

        self._propagate_skipped_nodes(
            plan=plan,
            failed_node_id=node_id,
        )

        self._refresh_ready_nodes(plan)

        return plan

    def _build_execution_nodes(
        self,
        graph: RenderGraph,
        execution_order: list[str],
        node_levels: dict[str, int],
    ) -> list[RenderExecutionNode]:
        node_map = {
            node.node_id: node
            for node in graph.nodes
        }

        execution_nodes: list[RenderExecutionNode] = []

        for execution_index, node_id in enumerate(
            execution_order
        ):
            source = node_map[node_id]

            execution_nodes.append(
                RenderExecutionNode(
                    node_id=source.node_id,
                    node_type=self._enum_value(
                        source.node_type
                    ),
                    stage=self._enum_value(
                        source.stage
                    ),
                    execution_level=node_levels[node_id],
                    execution_index=execution_index,
                    dependencies=list(
                        source.dependencies
                    ),
                    status=RenderNodeStatus.PENDING,
                    priority=source.priority,
                    metadata={
                        **source.metadata,
                        "source_graph_version": (
                            graph.version
                        ),
                    },
                )
            )

        return execution_nodes

    def _refresh_ready_nodes(
        self,
        plan: RenderExecutionPlan,
    ) -> None:
        node_map = {
            node.node_id: node
            for node in plan.nodes
        }

        for node in plan.nodes:
            if self._status_value(node.status) != (
                RenderNodeStatus.PENDING.value
            ):
                continue

            dependency_nodes = [
                node_map[dependency]
                for dependency in node.dependencies
                if dependency in node_map
            ]

            dependency_statuses = {
                self._status_value(
                    dependency.status
                )
                for dependency in dependency_nodes
            }

            if dependency_statuses.intersection(
                {
                    RenderNodeStatus.FAILED.value,
                    RenderNodeStatus.SKIPPED.value,
                }
            ):
                node.status = RenderNodeStatus.SKIPPED
                node.metadata = {
                    **node.metadata,
                    "skip_reason": (
                        "dependency_failed_or_skipped"
                    ),
                }
                continue

            if all(
                self._status_value(
                    dependency.status
                )
                == RenderNodeStatus.COMPLETED.value
                for dependency in dependency_nodes
            ):
                node.status = RenderNodeStatus.READY

    def _propagate_skipped_nodes(
        self,
        plan: RenderExecutionPlan,
        failed_node_id: str,
    ) -> None:
        dependents: dict[str, list[str]] = defaultdict(list)

        for node in plan.nodes:
            for dependency in node.dependencies:
                dependents[dependency].append(
                    node.node_id
                )

        node_map = {
            node.node_id: node
            for node in plan.nodes
        }

        stack = list(
            dependents.get(failed_node_id, [])
        )

        visited: set[str] = set()

        while stack:
            node_id = stack.pop()

            if node_id in visited:
                continue

            visited.add(node_id)

            node = node_map.get(node_id)

            if node is None:
                continue

            current_status = self._status_value(
                node.status
            )

            if current_status not in {
                RenderNodeStatus.COMPLETED.value,
                RenderNodeStatus.FAILED.value,
            }:
                node.status = RenderNodeStatus.SKIPPED
                node.metadata = {
                    **node.metadata,
                    "skip_reason": (
                        "upstream_dependency_failed"
                    ),
                    "failed_dependency": (
                        failed_node_id
                    ),
                }

            stack.extend(
                dependents.get(node_id, [])
            )

    def _require_node(
        self,
        plan: RenderExecutionPlan,
        node_id: str,
    ) -> RenderExecutionNode:
        node = next(
            (
                item
                for item in plan.nodes
                if item.node_id == node_id
            ),
            None,
        )

        if node is None:
            raise KeyError(
                f"Render execution node not found: {node_id}"
            )

        return node

    def _status_value(
        self,
        status,
    ) -> str:
        return (
            status.value
            if hasattr(status, "value")
            else str(status)
        )

    def _enum_value(
        self,
        value,
    ) -> str:
        return (
            value.value
            if hasattr(value, "value")
            else str(value)
        )