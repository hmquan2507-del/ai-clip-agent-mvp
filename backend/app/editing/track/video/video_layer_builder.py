from __future__ import annotations

from app.editing.track.models import TrackNode
from app.editing.track.video.effect_registry import classify_video_operation
from app.editing.track.video.layer_models import VideoLayer, VideoLayerEvent


class VideoLayerBuilder:
    def build_layers(
        self,
        nodes: list[TrackNode],
    ) -> list[VideoLayer]:
        layers = {
            "base": VideoLayer(layer_name="base", layer_type="base_video"),
            "camera_motion": VideoLayer(
                layer_name="camera_motion",
                layer_type="video_effect",
            ),
            "broll": VideoLayer(
                layer_name="broll",
                layer_type="visual_overlay",
            ),
            "overlay": VideoLayer(
                layer_name="overlay",
                layer_type="visual_overlay",
            ),
            "transition": VideoLayer(
                layer_name="transition",
                layer_type="transition",
            ),
        }

        for node in nodes:
            layer_key = classify_video_operation(
                operation=node.operation,
                track=node.track,
            )

            layer = layers.get(layer_key) or layers["base"]

            layer.add_event(
                VideoLayerEvent(
                    start_time=node.start_time,
                    end_time=node.end_time,
                    operation=node.operation,
                    parameters=node.parameters,
                    priority=node.priority,
                    source_node_id=node.node_id,
                    source_segment_id=node.source_segment_id,
                    reason=node.reason,
                )
            )

        for layer in layers.values():
            layer.events.sort(
                key=lambda event: (
                    event.start_time,
                    self._priority_rank(event.priority),
                    event.operation,
                )
            )

        return list(layers.values())

    def _priority_rank(self, priority: str) -> int:
        return {
            "high": 0,
            "medium": 1,
            "low": 2,
        }.get(priority, 99)