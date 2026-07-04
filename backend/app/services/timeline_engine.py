from __future__ import annotations

import json

from app.db.enums import (
    EditingPlanItemAction,
    TimelineClipType,
    TimelineTrackType,
)


class TimelineEngine:
    def build_from_editing_plan(self, editing_plan) -> dict:
        video_clips: list[dict] = []
        broll_clips: list[dict] = []
        subtitle_clips: list[dict] = []
        sound_clips: list[dict] = []

        cursor = 0.0

        items = sorted(
            editing_plan.items,
            key=lambda item: (item.start_time, item.end_time),
        )

        for item in items:
            duration = max(float(item.end_time) - float(item.start_time), 0)

            if duration <= 0:
                continue

            if item.action in {
                EditingPlanItemAction.KEEP,
                EditingPlanItemAction.HOOK,
                EditingPlanItemAction.HIGHLIGHT,
            }:
                video_clips.append(
                    {
                        "type": TimelineClipType.SOURCE,
                        "source_start": float(item.start_time),
                        "source_end": float(item.end_time),
                        "timeline_start": cursor,
                        "timeline_end": cursor + duration,
                        "metadata": {
                            "editing_action": item.action.value,
                            "reason": item.reason,
                            "priority": item.priority,
                        },
                    }
                )

                subtitle_clips.append(
                    {
                        "type": TimelineClipType.SUBTITLE,
                        "timeline_start": cursor,
                        "timeline_end": cursor + duration,
                        "text": item.reason or "",
                        "metadata": {
                            "source_start": float(item.start_time),
                            "source_end": float(item.end_time),
                        },
                    }
                )

                cursor += duration

            elif item.action == EditingPlanItemAction.BROLL:
                broll_clips.append(
                    {
                        "type": TimelineClipType.BROLL,
                        "timeline_start": cursor,
                        "timeline_end": cursor + duration,
                        "metadata": {
                            "source_start": float(item.start_time),
                            "source_end": float(item.end_time),
                            "reason": item.reason,
                            "priority": item.priority,
                        },
                    }
                )

            elif item.action == EditingPlanItemAction.SOUND_EFFECT:
                sound_clips.append(
                    {
                        "type": TimelineClipType.SOUND_EFFECT,
                        "timeline_start": cursor,
                        "timeline_end": min(cursor + 1.0, cursor + duration),
                        "metadata": {
                            "reason": item.reason,
                            "priority": item.priority,
                        },
                    }
                )

        return {
            "duration_seconds": cursor,
            "tracks": [
                {
                    "type": TimelineTrackType.VIDEO,
                    "name": "Main Video",
                    "position": 0,
                    "clips": video_clips,
                },
                {
                    "type": TimelineTrackType.SUBTITLE,
                    "name": "Subtitles",
                    "position": 1,
                    "clips": subtitle_clips,
                },
                {
                    "type": TimelineTrackType.BROLL,
                    "name": "B-roll",
                    "position": 2,
                    "clips": broll_clips,
                },
                {
                    "type": TimelineTrackType.SOUND_EFFECT,
                    "name": "Sound Effects",
                    "position": 3,
                    "clips": sound_clips,
                },
            ],
        }

    def dumps_metadata(self, metadata: dict | None) -> str | None:
        if metadata is None:
            return None

        return json.dumps(metadata, ensure_ascii=False)