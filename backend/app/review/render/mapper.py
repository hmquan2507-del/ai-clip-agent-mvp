from __future__ import annotations

from copy import deepcopy

from app.review.editing.models import EditableTimeline


class ReviewTimelineRenderMapper:
    def map(self, timeline: EditableTimeline) -> dict:
        payload = timeline.to_dict()
        payload["tracks"] = [
            track for track in payload.get("tracks", [])
            if track.get("enabled", True) and not track.get("hidden", False)
        ]
        for track in payload["tracks"]:
            track["clips"] = [
                clip for clip in track.get("clips", [])
                if clip.get("enabled", True)
            ]
            track["clip_count"] = len(track["clips"])
        payload["track_count"] = len(payload["tracks"])
        payload["clip_count"] = sum(len(track["clips"]) for track in payload["tracks"])
        return deepcopy(payload)
