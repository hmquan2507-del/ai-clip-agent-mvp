from __future__ import annotations

from app.editing.track.audio.audio_layer_builder import AudioLayerBuilder
from app.editing.track.audio.audio_rules import DEFAULT_MIX_ORDER
from app.editing.track.audio.models import AudioTrack
from app.editing.track.composer_base import BaseTrackComposer
from app.editing.track.models import TrackContext, TrackNode


class AudioTrackComposer(BaseTrackComposer):
    track_name = "audio"

    def __init__(self):
        self.layer_builder = AudioLayerBuilder()

    def compose(self, context: TrackContext) -> AudioTrack:
        nodes = self._collect_audio_nodes(context)
        layers = self.layer_builder.build_layers(nodes)

        return AudioTrack(
            production_id=context.production_id,
            layers=layers,
            mix_order=DEFAULT_MIX_ORDER,
            metadata={
                "composer": "audio_track_composer",
                "input_nodes": len(nodes),
                "layer_count": len(layers),
                "layer_event_counts": {
                    layer.layer_name: len(layer.events)
                    for layer in layers
                },
            },
        )

    def _collect_audio_nodes(
        self,
        context: TrackContext,
    ) -> list[TrackNode]:
        nodes: list[TrackNode] = []

        nodes.extend(context.audio_nodes)
        nodes.extend(context.music_nodes)
        nodes.extend(context.sfx_nodes)

        for custom_nodes in context.custom_nodes.values():
            for node in custom_nodes:
                if node.track in {"audio", "music", "sfx"}:
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