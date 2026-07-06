from __future__ import annotations

from typing import Any

from app.editing.track.composer_base import BaseTrackComposer
from app.editing.track.models import TrackContext, TrackNode
from app.editing.track.subtitle.models import SubtitleEvent, SubtitleTrack
from app.editing.track.subtitle.subtitle_style_rules import (
    build_subtitle_style,
    subtitle_animation,
)
from app.editing.track.subtitle.subtitle_text_resolver import SubtitleTextResolver


class SubtitleTrackComposer(BaseTrackComposer):
    track_name = "subtitle"

    def __init__(self):
        self.text_resolver = SubtitleTextResolver()

    def compose(
        self,
        context: TrackContext,
        segments: list[dict[str, Any]] | None = None,
    ) -> SubtitleTrack:
        safe_segments = segments or []
        events: list[SubtitleEvent] = []

        for node in context.subtitle_nodes:
            event = self._compose_node(
                node=node,
                segments=safe_segments,
            )

            if event is not None:
                events.append(event)

        events = self._deduplicate(events)
        events = self._sort_events(events)

        return SubtitleTrack(
            production_id=context.production_id,
            events=events,
            metadata={
                "composer": "subtitle_track_composer",
                "input_nodes": len(context.subtitle_nodes),
                "event_count": len(events),
            },
        )

    def _compose_node(
        self,
        node: TrackNode,
        segments: list[dict[str, Any]],
    ) -> SubtitleEvent | None:
        node_dict = node.to_dict()

        text = self.text_resolver.resolve(
            node=node_dict,
            segments=segments,
        )

        if not text:
            return None

        style = build_subtitle_style(
            node_parameters=node.parameters,
            priority=node.priority,
        )

        animation = subtitle_animation(
            node_parameters=node.parameters,
            priority=node.priority,
        )

        return SubtitleEvent(
            start_time=node.start_time,
            end_time=node.end_time,
            text=text,
            style=style,
            animation=animation,
            priority=node.priority,
            source_segment_id=node.source_segment_id,
            source_node_id=node.node_id,
            reason=node.reason,
        )

    def _deduplicate(
        self,
        events: list[SubtitleEvent],
    ) -> list[SubtitleEvent]:
        seen: set[tuple[float, float, str, str | None]] = set()
        unique: list[SubtitleEvent] = []

        for event in events:
            key = (
                round(event.start_time, 2),
                round(event.end_time, 2),
                event.text,
                event.source_segment_id,
            )

            if key in seen:
                continue

            seen.add(key)
            unique.append(event)

        return unique

    def _sort_events(
        self,
        events: list[SubtitleEvent],
    ) -> list[SubtitleEvent]:
        return sorted(
            events,
            key=lambda event: (
                event.start_time,
                self._priority_rank(event.priority),
                event.end_time,
            ),
        )

    def _priority_rank(self, priority: str) -> int:
        return {
            "high": 0,
            "medium": 1,
            "low": 2,
        }.get(priority, 99)