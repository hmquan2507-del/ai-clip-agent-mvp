from __future__ import annotations

from app.editing.execution.conflict.models import Conflict
from app.editing.execution.graph.models import ExecutionGraph, ExecutionNode


class ConflictDetector:
    def detect(self, graph: ExecutionGraph) -> list[Conflict]:
        conflicts: list[Conflict] = []

        conflicts.extend(self._detect_invalid_timeline(graph))
        conflicts.extend(self._detect_same_track_overlap(graph))
        conflicts.extend(self._detect_duplicate_operations(graph))
        conflicts.extend(self._detect_priority_inversion(graph))

        return conflicts

    def _detect_invalid_timeline(self, graph: ExecutionGraph) -> list[Conflict]:
        conflicts: list[Conflict] = []

        for node in graph.nodes:
            if node.start_time < 0:
                conflicts.append(
                    Conflict(
                        conflict_id=f"conflict_{len(conflicts)}",
                        conflict_type="invalid_timeline",
                        severity="high",
                        left_node_id=node.node_id,
                        reason="node_start_time_negative",
                    )
                )

            if node.end_time < node.start_time:
                conflicts.append(
                    Conflict(
                        conflict_id=f"conflict_{len(conflicts)}",
                        conflict_type="invalid_timeline",
                        severity="high",
                        left_node_id=node.node_id,
                        reason="node_end_before_start",
                    )
                )

        return conflicts

    def _detect_same_track_overlap(self, graph: ExecutionGraph) -> list[Conflict]:
        conflicts: list[Conflict] = []

        nodes = graph.nodes

        for left_index, left in enumerate(nodes):
            for right in nodes[left_index + 1 :]:
                if left.track != right.track:
                    continue

                if left.track in {"global", "timeline"}:
                    continue

                if not self._overlap(left, right):
                    continue

                conflicts.append(
                    Conflict(
                        conflict_id=f"conflict_overlap_{len(conflicts)}",
                        conflict_type="same_track_overlap",
                        severity="medium",
                        left_node_id=left.node_id,
                        right_node_id=right.node_id,
                        reason=f"overlap_on_track:{left.track}",
                        metadata={
                            "track": left.track,
                            "left_operation": left.operation,
                            "right_operation": right.operation,
                        },
                    )
                )

        return conflicts

    def _detect_duplicate_operations(self, graph: ExecutionGraph) -> list[Conflict]:
        conflicts: list[Conflict] = []
        seen: dict[tuple[str, str, float, float, str | None], str] = {}

        for node in graph.nodes:
            key = (
                node.track,
                node.operation,
                round(node.start_time, 2),
                round(node.end_time, 2),
                node.source_segment_id,
            )

            if key in seen:
                conflicts.append(
                    Conflict(
                        conflict_id=f"conflict_duplicate_{len(conflicts)}",
                        conflict_type="duplicate_operation",
                        severity="low",
                        left_node_id=seen[key],
                        right_node_id=node.node_id,
                        reason="duplicate_same_operation_same_time",
                    )
                )
            else:
                seen[key] = node.node_id

        return conflicts

    def _detect_priority_inversion(self, graph: ExecutionGraph) -> list[Conflict]:
        conflicts: list[Conflict] = []

        for edge in graph.edges:
            source = self._find_node(graph, edge.from_node_id)
            target = self._find_node(graph, edge.to_node_id)

            if source is None or target is None:
                continue

            if source.weight < target.weight and edge.dependency_type in {
                "global_style_dependency",
                "timeline_pacing_dependency",
            }:
                conflicts.append(
                    Conflict(
                        conflict_id=f"conflict_priority_{len(conflicts)}",
                        conflict_type="priority_inversion",
                        severity="low",
                        left_node_id=source.node_id,
                        right_node_id=target.node_id,
                        reason=f"lower_weight_source_before_higher_weight_target:{edge.dependency_type}",
                    )
                )

        return conflicts

    def _find_node(
        self,
        graph: ExecutionGraph,
        node_id: str,
    ) -> ExecutionNode | None:
        for node in graph.nodes:
            if node.node_id == node_id:
                return node

        return None

    def _overlap(
        self,
        left: ExecutionNode,
        right: ExecutionNode,
    ) -> bool:
        return left.start_time < right.end_time and right.start_time < left.end_time