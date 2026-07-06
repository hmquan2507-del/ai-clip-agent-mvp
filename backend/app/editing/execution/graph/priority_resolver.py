from __future__ import annotations

from app.editing.execution.graph.models import ExecutionGraph, ExecutionNode


class PriorityResolver:
    def sort_nodes(self, graph: ExecutionGraph) -> list[ExecutionNode]:
        return sorted(
            graph.nodes,
            key=lambda node: (
                node.start_time,
                self._priority_rank(node.priority),
                node.track,
                node.operation,
            ),
        )

    def _priority_rank(self, priority: str) -> int:
        return {
            "high": 0,
            "medium": 1,
            "low": 2,
        }.get(priority, 99)