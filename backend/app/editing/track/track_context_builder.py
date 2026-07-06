from __future__ import annotations

from typing import Any

from app.editing.track.models import TrackContext, TrackNode
from app.editing.track.track_classifier import TrackClassifier


class TrackContextBuilder:
    def __init__(self):
        self.classifier = TrackClassifier()

    def build(
        self,
        production_id: str,
        optimized_execution_graph: dict[str, Any],
    ) -> TrackContext:
        context = TrackContext(
            production_id=production_id,
            metadata={
                "builder": "track_context_builder",
            },
        )

        nodes = optimized_execution_graph.get("nodes", [])
        if not isinstance(nodes, list):
            nodes = []

        for raw_node in nodes:
            if not isinstance(raw_node, dict):
                continue

            node = self.classifier.to_track_node(raw_node)

            if node is None:
                continue

            self._add_node(context, node)

        self._sort_context(context)

        context.metadata["total_nodes"] = len(context.all_nodes())
        context.metadata["track_counts"] = {
            "global": len(context.global_nodes),
            "timeline": len(context.timeline_nodes),
            "video": len(context.video_nodes),
            "camera_motion": len(context.camera_nodes),
            "subtitle": len(context.subtitle_nodes),
            "broll": len(context.broll_nodes),
            "audio": len(context.audio_nodes),
            "sfx": len(context.sfx_nodes),
            "custom": sum(len(nodes) for nodes in context.custom_nodes.values()),
            "music": len(context.music_nodes),
        }

        return context

    def _add_node(
        self,
        context: TrackContext,
        node: TrackNode,
    ) -> None:
        if node.track == "global":
            context.global_nodes.append(node)
            return

        if node.track == "timeline":
            context.timeline_nodes.append(node)
            return

        if node.track == "video":
            context.video_nodes.append(node)
            return

        if node.track == "camera_motion":
            context.camera_nodes.append(node)
            return

        if node.track == "subtitle":
            context.subtitle_nodes.append(node)
            return

        if node.track == "broll":
            context.broll_nodes.append(node)
            return

        if node.track == "audio":
            context.audio_nodes.append(node)
            return
        if node.track == "music":
            context.music_nodes.append(node)
            return
        if node.track == "sfx":
            context.sfx_nodes.append(node)
            return

        context.custom_nodes.setdefault(node.track, []).append(node)

    def _sort_context(self, context: TrackContext) -> None:
        context.global_nodes = self._sort_nodes(context.global_nodes)
        context.timeline_nodes = self._sort_nodes(context.timeline_nodes)
        context.video_nodes = self._sort_nodes(context.video_nodes)
        context.camera_nodes = self._sort_nodes(context.camera_nodes)
        context.subtitle_nodes = self._sort_nodes(context.subtitle_nodes)
        context.broll_nodes = self._sort_nodes(context.broll_nodes)
        context.audio_nodes = self._sort_nodes(context.audio_nodes)
        context.sfx_nodes = self._sort_nodes(context.sfx_nodes)
        context.music_nodes = self._sort_nodes(context.music_nodes)

        for key in list(context.custom_nodes.keys()):
            context.custom_nodes[key] = self._sort_nodes(context.custom_nodes[key])

    def _sort_nodes(self, nodes: list[TrackNode]) -> list[TrackNode]:
        return sorted(
            nodes,
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