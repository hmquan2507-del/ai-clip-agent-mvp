from __future__ import annotations

from collections import deque
from typing import Any


class DependencyScheduler:
    def schedule(
        self,
        render_graph: dict[str, Any],
    ) -> list[dict[str, Any]]:
        nodes = self._safe_nodes(render_graph)
        edges = self._safe_edges(render_graph)

        node_by_id = {
            str(node.get("node_id")): node
            for node in nodes
            if node.get("node_id")
        }

        in_degree: dict[str, int] = {
            node_id: 0 for node_id in node_by_id
        }

        adjacency: dict[str, list[str]] = {
            node_id: [] for node_id in node_by_id
        }

        for edge in edges:
            from_node_id = str(edge.get("from_node_id") or "")
            to_node_id = str(edge.get("to_node_id") or "")

            if from_node_id not in node_by_id or to_node_id not in node_by_id:
                continue

            adjacency[from_node_id].append(to_node_id)
            in_degree[to_node_id] += 1

        ready = deque(
            sorted(
                [
                    node_id
                    for node_id, degree in in_degree.items()
                    if degree == 0
                ],
                key=lambda node_id: self._node_sort_key(node_by_id[node_id]),
            )
        )

        scheduled: list[dict[str, Any]] = []
        order_index = 0

        while ready:
            same_level = list(ready)
            ready.clear()

            same_level.sort(
                key=lambda node_id: self._node_sort_key(node_by_id[node_id])
            )

            for node_id in same_level:
                node = node_by_id[node_id]
                scheduled.append(
                    {
                        "node": node,
                        "order_index": order_index,
                        "parallel_group": order_index,
                        "can_run_parallel": len(same_level) > 1,
                    }
                )

                for child_id in adjacency.get(node_id, []):
                    in_degree[child_id] -= 1

                    if in_degree[child_id] == 0:
                        ready.append(child_id)

            order_index += 1

        if len(scheduled) != len(node_by_id):
            unresolved = [
                node_id
                for node_id in node_by_id
                if node_id not in {
                    item["node"]["node_id"] for item in scheduled
                }
            ]

            for node_id in unresolved:
                node = node_by_id[node_id]
                scheduled.append(
                    {
                        "node": node,
                        "order_index": order_index,
                        "parallel_group": order_index,
                        "can_run_parallel": False,
                        "metadata": {
                            "warning": "scheduled_with_unresolved_dependency",
                        },
                    }
                )
                order_index += 1

        return scheduled

    def _safe_nodes(
        self,
        render_graph: dict[str, Any],
    ) -> list[dict[str, Any]]:
        nodes = render_graph.get("nodes", [])
        if not isinstance(nodes, list):
            return []

        return [node for node in nodes if isinstance(node, dict)]

    def _safe_edges(
        self,
        render_graph: dict[str, Any],
    ) -> list[dict[str, Any]]:
        edges = render_graph.get("edges", [])
        if not isinstance(edges, list):
            return []

        return [edge for edge in edges if isinstance(edge, dict)]

    def _node_sort_key(self, node: dict[str, Any]) -> tuple[int, str, str]:
        return (
            self._priority_rank(str(node.get("priority") or "medium")),
            str(node.get("node_type") or ""),
            str(node.get("operation") or ""),
        )

    def _priority_rank(self, priority: str) -> int:
        return {
            "high": 0,
            "medium": 1,
            "low": 2,
        }.get(priority, 99)