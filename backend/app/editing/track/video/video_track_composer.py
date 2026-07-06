from __future__ import annotations

from app.editing.track.composer_base import BaseTrackComposer
from app.editing.track.models import TrackContext, TrackNode
from app.editing.track.video.models import VideoTrack
from app.editing.track.video.video_layer_builder import VideoLayerBuilder


class VideoTrackComposer(BaseTrackComposer):
    track_name = "video"

    def __init__(self):
        self.layer_builder = VideoLayerBuilder()

    def compose(self, context: TrackContext) -> VideoTrack:
        nodes = self._collect_video_nodes(context)
        layers = self.layer_builder.build_layers(nodes)

        return VideoTrack(
            production_id=context.production_id,
            layers=layers,
            metadata={
                "composer": "video_track_composer",
                "input_nodes": len(nodes),
                "layer_count": len(layers),
                "layer_event_counts": {
                    layer.layer_name: len(layer.events)
                    for layer in layers
                },
            },
        )

    def _collect_video_nodes(
        self,
        context: TrackContext,
    ) -> list[TrackNode]:
        nodes: list[TrackNode] = []

        nodes.extend(context.video_nodes)
        nodes.extend(context.camera_nodes)
        nodes.extend(context.broll_nodes)

        for custom_nodes in context.custom_nodes.values():
            for node in custom_nodes:
                if node.track in {"video", "camera_motion", "broll"}:
                    nodes.append(node)

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