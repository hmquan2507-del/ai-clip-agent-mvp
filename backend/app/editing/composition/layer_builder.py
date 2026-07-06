from __future__ import annotations

from typing import Any

from app.editing.composition.models import CompositionLayer, TrackArtifact


class CompositionLayerBuilder:
    def build_layers(
        self,
        artifacts: list[TrackArtifact],
    ) -> list[CompositionLayer]:
        layers: list[CompositionLayer] = []

        for artifact in artifacts:
            if artifact.track_key == "subtitle":
                layers.extend(self._build_subtitle_layers(artifact))
                continue

            if artifact.track_key == "video":
                layers.extend(self._build_video_layers(artifact))
                continue

            if artifact.track_key == "audio":
                layers.extend(self._build_audio_layers(artifact))
                continue

            layers.append(
                CompositionLayer(
                    layer_key=f"{artifact.track_key}_base",
                    layer_type="custom",
                    track_key=artifact.track_key,
                    events=[],
                    metadata={
                        "source": "unknown_track_artifact",
                    },
                )
            )

        return layers

    def _build_subtitle_layers(
        self,
        artifact: TrackArtifact,
    ) -> list[CompositionLayer]:
        events = artifact.payload.get("events", [])

        if not isinstance(events, list):
            events = []

        return [
            CompositionLayer(
                layer_key="subtitle_main",
                layer_type="subtitle",
                track_key="subtitle",
                events=[
                    event for event in events if isinstance(event, dict)
                ],
                metadata={
                    "source_track": "subtitle_track",
                    "event_count": len(events),
                },
            )
        ]

    def _build_video_layers(
        self,
        artifact: TrackArtifact,
    ) -> list[CompositionLayer]:
        layers: list[CompositionLayer] = []
        raw_layers = artifact.payload.get("layers", [])

        if not isinstance(raw_layers, list):
            return layers

        for layer in raw_layers:
            if not isinstance(layer, dict):
                continue

            layer_name = str(layer.get("layer_name") or "video_layer")
            layer_type = str(layer.get("layer_type") or "video")
            events = layer.get("events", [])

            if not isinstance(events, list):
                events = []

            layers.append(
                CompositionLayer(
                    layer_key=f"video_{layer_name}",
                    layer_type=layer_type,
                    track_key="video",
                    events=[
                        event for event in events if isinstance(event, dict)
                    ],
                    metadata={
                        "source_track": "video_track",
                        "source_layer": layer_name,
                        "event_count": len(events),
                    },
                )
            )

        return layers

    def _build_audio_layers(
        self,
        artifact: TrackArtifact,
    ) -> list[CompositionLayer]:
        layers: list[CompositionLayer] = []
        raw_layers = artifact.payload.get("layers", [])

        if not isinstance(raw_layers, list):
            return layers

        for layer in raw_layers:
            if not isinstance(layer, dict):
                continue

            layer_name = str(layer.get("layer_name") or "audio_layer")
            layer_type = str(layer.get("layer_type") or "audio")
            events = layer.get("events", [])

            if not isinstance(events, list):
                events = []

            layers.append(
                CompositionLayer(
                    layer_key=f"audio_{layer_name}",
                    layer_type=layer_type,
                    track_key="audio",
                    events=[
                        event for event in events if isinstance(event, dict)
                    ],
                    metadata={
                        "source_track": "audio_track",
                        "source_layer": layer_name,
                        "event_count": len(events),
                    },
                )
            )

        return layers