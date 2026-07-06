from __future__ import annotations

from app.editing.execution.conflict.models import Conflict, ConflictResolution
from app.editing.execution.graph.models import ExecutionGraph, ExecutionNode


class ConflictRules:
    def resolve(
        self,
        graph: ExecutionGraph,
        conflict: Conflict,
    ) -> ConflictResolution:
        if conflict.conflict_type == "duplicate_operation":
            return self._resolve_duplicate(graph, conflict)

        if conflict.conflict_type == "same_track_overlap":
            return self._resolve_overlap(graph, conflict)

        if conflict.conflict_type == "invalid_timeline":
            return self._resolve_invalid_timeline(graph, conflict)

        if conflict.conflict_type == "priority_inversion":
            return ConflictResolution(
                conflict_id=conflict.conflict_id,
                action="keep",
                target_node_id=conflict.left_node_id,
                reason="priority_inversion_logged_only",
            )

        return ConflictResolution(
            conflict_id=conflict.conflict_id,
            action="keep",
            target_node_id=conflict.left_node_id,
            reason="no_rule_matched",
        )

    def _resolve_duplicate(
        self,
        graph: ExecutionGraph,
        conflict: Conflict,
    ) -> ConflictResolution:
        left = self._find_node(graph, conflict.left_node_id)
        right = self._find_node(graph, conflict.right_node_id)

        if left is None or right is None:
            return ConflictResolution(
                conflict_id=conflict.conflict_id,
                action="keep",
                reason="duplicate_node_missing",
            )

        loser = right if left.weight >= right.weight else left
        winner = left if loser is right else right

        return ConflictResolution(
            conflict_id=conflict.conflict_id,
            action="remove_node",
            target_node_id=loser.node_id,
            replacement_node_id=winner.node_id,
            reason="remove_lower_weight_duplicate",
        )

    def _resolve_overlap(
        self,
        graph: ExecutionGraph,
        conflict: Conflict,
    ) -> ConflictResolution:
        left = self._find_node(graph, conflict.left_node_id)
        right = self._find_node(graph, conflict.right_node_id)

        if left is None or right is None:
            return ConflictResolution(
                conflict_id=conflict.conflict_id,
                action="keep",
                reason="overlap_node_missing",
            )

        if left.weight == right.weight:
            loser = right
            winner = left
        else:
            loser = right if left.weight > right.weight else left
            winner = left if loser is right else right

        return ConflictResolution(
            conflict_id=conflict.conflict_id,
            action="remove_node",
            target_node_id=loser.node_id,
            replacement_node_id=winner.node_id,
            reason="remove_lower_weight_overlap",
            metadata={
                "winner": winner.node_id,
                "loser": loser.node_id,
            },
        )

    def _resolve_invalid_timeline(
        self,
        graph: ExecutionGraph,
        conflict: Conflict,
    ) -> ConflictResolution:
        return ConflictResolution(
            conflict_id=conflict.conflict_id,
            action="remove_node",
            target_node_id=conflict.left_node_id,
            reason="remove_invalid_timeline_node",
        )

    def _find_node(
        self,
        graph: ExecutionGraph,
        node_id: str | None,
    ) -> ExecutionNode | None:
        if node_id is None:
            return None

        for node in graph.nodes:
            if node.node_id == node_id:
                return node

        return None