from __future__ import annotations

from typing import Any


class AssetManifestBuilder:
    def build_manifest(
        self,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "source_video": self._find_source_video(metadata),
            "subtitle": self._has_subtitle_track(metadata),
            "broll": self._has_broll_layer(metadata),
            "music": self._has_music_layer(metadata),
            "sfx": self._has_sfx_layer(metadata),
        }

    def _find_source_video(
        self,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        production = metadata.get("production", {})

        if isinstance(production, dict):
            source_video_path = production.get("source_video_path")
            source_video_uri = production.get("source_video_uri")

            if source_video_path or source_video_uri:
                return {
                    "exists": True,
                    "local_path": source_video_path,
                    "uri": source_video_uri,
                }

        return {
            "exists": False,
            "local_path": None,
            "uri": None,
        }

    def _has_subtitle_track(
        self,
        metadata: dict[str, Any],
    ) -> bool:
        subtitle_track = metadata.get("subtitle_track", {})
        if not isinstance(subtitle_track, dict):
            return False

        events = subtitle_track.get("events", [])
        return isinstance(events, list) and len(events) > 0

    def _has_broll_layer(
        self,
        metadata: dict[str, Any],
    ) -> bool:
        video_track = metadata.get("video_track", {})
        return self._track_has_layer(video_track, "broll")

    def _has_music_layer(
        self,
        metadata: dict[str, Any],
    ) -> bool:
        audio_track = metadata.get("audio_track", {})
        return self._track_has_layer(audio_track, "music")

    def _has_sfx_layer(
        self,
        metadata: dict[str, Any],
    ) -> bool:
        audio_track = metadata.get("audio_track", {})
        return self._track_has_layer(audio_track, "sfx")

    def _track_has_layer(
        self,
        track_payload: Any,
        layer_name: str,
    ) -> bool:
        if not isinstance(track_payload, dict):
            return False

        layers = track_payload.get("layers", [])
        if not isinstance(layers, list):
            return False

        for layer in layers:
            if not isinstance(layer, dict):
                continue

            if layer.get("layer_name") != layer_name:
                continue

            events = layer.get("events", [])
            return isinstance(events, list) and len(events) > 0

        return False