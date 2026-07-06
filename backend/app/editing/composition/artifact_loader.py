from __future__ import annotations

from typing import Any

from app.editing.composition.models import TrackArtifact


class TrackArtifactLoader:
    def load_many(
        self,
        metadata: dict[str, Any],
    ) -> list[TrackArtifact]:
        artifacts: list[TrackArtifact] = []

        for track_key, metadata_key in self._track_metadata_map().items():
            payload = metadata.get(metadata_key)

            if not isinstance(payload, dict):
                continue

            artifacts.append(
                TrackArtifact(
                    track_key=track_key,
                    payload=payload,
                    metadata={
                        "metadata_key": metadata_key,
                    },
                )
            )

        return artifacts

    def _track_metadata_map(self) -> dict[str, str]:
        return {
            "subtitle": "subtitle_track",
            "video": "video_track",
            "audio": "audio_track",
        }