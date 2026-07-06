from __future__ import annotations

from app.editing.track.audio.audio_effect_registry import classify_audio_operation
from app.editing.track.audio.audio_rules import default_master_chain
from app.editing.track.audio.layer_models import AudioLayer, AudioLayerEvent
from app.editing.track.models import TrackNode


class AudioLayerBuilder:
    def build_layers(
        self,
        nodes: list[TrackNode],
    ) -> list[AudioLayer]:
        layers = {
            "voice": AudioLayer(layer_name="voice", layer_type="voice"),
            "music": AudioLayer(layer_name="music", layer_type="music"),
            "sfx": AudioLayer(layer_name="sfx", layer_type="sound_effect"),
            "ducking": AudioLayer(layer_name="ducking", layer_type="mix_control"),
            "master": AudioLayer(layer_name="master", layer_type="master_bus"),
        }

        for node in nodes:
            layer_key = classify_audio_operation(
                operation=node.operation,
                track=node.track,
            )

            layer = layers.get(layer_key) or layers["voice"]

            layer.add_event(
                AudioLayerEvent(
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

            if layer_key == "sfx":
                layers["ducking"].add_event(
                    AudioLayerEvent(
                        start_time=node.start_time,
                        end_time=node.end_time,
                        operation="duck_music",
                        parameters={
                            "duck_db": -6,
                            "attack_ms": 80,
                            "release_ms": 250,
                        },
                        priority=node.priority,
                        source_node_id=node.node_id,
                        source_segment_id=node.source_segment_id,
                        reason="auto_duck_music_for_sfx",
                    )
                )

        self._add_default_master_chain(layers["master"])

        for layer in layers.values():
            layer.events.sort(
                key=lambda event: (
                    event.start_time,
                    self._priority_rank(event.priority),
                    event.operation,
                )
            )

        return list(layers.values())

    def _add_default_master_chain(self, master_layer: AudioLayer) -> None:
        for item in default_master_chain():
            master_layer.add_event(
                AudioLayerEvent(
                    start_time=0.0,
                    end_time=0.0,
                    operation=item["operation"],
                    parameters=item["parameters"],
                    priority="high",
                    reason="default_master_chain",
                )
            )

    def _priority_rank(self, priority: str) -> int:
        return {
            "high": 0,
            "medium": 1,
            "low": 2,
        }.get(priority, 99)