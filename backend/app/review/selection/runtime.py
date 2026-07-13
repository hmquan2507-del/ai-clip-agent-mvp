from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable

from app.review.selection.enums import (
    TimelineSelectionEventType,
    TimelineSelectionFocus,
    TimelineSelectionMode,
)
from app.review.selection.models import (
    TimelineSelectionCatalog,
    TimelineSelectionEvent,
    TimelineSelectionResult,
    TimelineSelectionState,
    TimelineTimeRange,
    utc_now_iso,
)
from app.review.selection.validator import (
    TimelineSelectionValidator,
)


TimelineSelectionEventCallback = Callable[
    [TimelineSelectionEvent],
    None,
]


class TimelineSelectionRuntime:
    def __init__(
        self,
        catalog: TimelineSelectionCatalog,
        *,
        validator: (
            TimelineSelectionValidator | None
        ) = None,
        event_callback: (
            TimelineSelectionEventCallback | None
        ) = None,
    ):
        self.catalog = deepcopy(catalog)
        self.validator = (
            validator
            or TimelineSelectionValidator()
        )
        self.event_callback = event_callback

        self._state = TimelineSelectionState(
            production_id=(
                catalog.production_id
            ),
            metadata={
                "runtime": (
                    "TimelineSelectionRuntime"
                ),
                "timeline_duration": (
                    catalog.duration
                ),
                "fps": catalog.fps,
            },
        )

        self._initial_state = deepcopy(
            self._state
        )

        self._events: list[
            TimelineSelectionEvent
        ] = []

        self._emit(
            TimelineSelectionEventType
            .SESSION_CREATED,
            metadata={
                "track_count": len(
                    catalog.tracks
                ),
                "clip_count": len(
                    catalog.clips
                ),
            },
        )

    def synchronize_catalog(
        self,
        catalog: TimelineSelectionCatalog,
    ) -> TimelineSelectionResult:
        if (
            catalog.production_id
            != self.catalog.production_id
        ):
            return self._fail(
                "Selection catalog production_id "
                "does not match runtime."
            )

        previous_track_ids = set(
            self._state.selected_track_ids
        )
        previous_clip_ids = set(
            self._state.selected_clip_ids
        )

        next_catalog = deepcopy(catalog)

        selected_track_ids = [
            track_id
            for track_id
            in self._state.selected_track_ids
            if track_id
            in next_catalog.track_ids
        ]

        selected_clip_ids = [
            clip_id
            for clip_id
            in self._state.selected_clip_ids
            if clip_id
            in next_catalog.clip_ids
        ]

        for clip_id in selected_clip_ids:
            clip = next_catalog.get_clip(
                clip_id
            )

            if (
                clip is not None
                and clip.track_id
                not in selected_track_ids
            ):
                selected_track_ids.append(
                    clip.track_id
                )

        self.catalog = next_catalog

        self._state.selected_track_ids = (
            selected_track_ids
        )
        self._state.selected_clip_ids = (
            selected_clip_ids
        )

        if (
            self._state.active_clip_id
            not in self.catalog.clip_ids
        ):
            self._state.active_clip_id = None

        if self._state.active_clip_id:
            active_clip = self.catalog.get_clip(
                self._state.active_clip_id
            )
            self._state.active_track_id = (
                active_clip.track_id
                if active_clip
                else None
            )
        elif (
            self._state.active_track_id
            not in self.catalog.track_ids
        ):
            self._state.active_track_id = None

        if (
            self._state.hovered_clip_id
            not in self.catalog.clip_ids
        ):
            self._state.hovered_clip_id = None

        if self._state.hovered_clip_id:
            hovered_clip = self.catalog.get_clip(
                self._state.hovered_clip_id
            )
            self._state.hovered_track_id = (
                hovered_clip.track_id
                if hovered_clip
                else None
            )
        elif (
            self._state.hovered_track_id
            not in self.catalog.track_ids
        ):
            self._state.hovered_track_id = None

        self._set_cursor_value(
            self._state.cursor_time
        )

        if self._state.selected_range:
            if self.catalog.duration <= 0:
                self._state.selected_range = None
            else:
                range_start = min(
                    self.catalog.duration,
                    self._state
                    .selected_range.start_time,
                )
                range_end = min(
                    self.catalog.duration,
                    self._state
                    .selected_range.end_time,
                )

                self._state.selected_range = (
                    TimelineTimeRange(
                        start_time=range_start,
                        end_time=range_end,
                    )
                )

        self._state.metadata[
            "timeline_duration"
        ] = self.catalog.duration
        self._state.metadata["fps"] = (
            self.catalog.fps
        )

        self._recalculate_mode()

        if (
            self._state.focus
            == TimelineSelectionFocus.CLIP
            and not self._state
            .selected_clip_ids
        ):
            self._state.focus = (
                TimelineSelectionFocus.TRACK
                if self._state
                .selected_track_ids
                else TimelineSelectionFocus
                .TIMELINE
            )

        self._touch()

        removed_track_ids = sorted(
            previous_track_ids
            - set(selected_track_ids)
        )
        removed_clip_ids = sorted(
            previous_clip_ids
            - set(selected_clip_ids)
        )

        event = self._emit(
            TimelineSelectionEventType
            .CATALOG_SYNCHRONIZED,
            metadata={
                "track_count": len(
                    self.catalog.tracks
                ),
                "clip_count": len(
                    self.catalog.clips
                ),
                "removed_track_ids": (
                    removed_track_ids
                ),
                "removed_clip_ids": (
                    removed_clip_ids
                ),
            },
        )

        return self._success(event)

    @property
    def state(
        self,
    ) -> TimelineSelectionState:
        return deepcopy(self._state)

    @property
    def events(
        self,
    ) -> list[TimelineSelectionEvent]:
        return list(self._events)

    def select_track(
        self,
        track_id: str,
        *,
        additive: bool = False,
    ) -> TimelineSelectionResult:
        error = self.validator.validate_track(
            self.catalog,
            track_id,
        )

        if error:
            return self._fail(error)

        if additive:
            selected = list(
                self._state.selected_track_ids
            )

            if track_id in selected:
                selected.remove(track_id)
            else:
                selected.append(track_id)

            self._state.selected_track_ids = (
                self._unique(selected)
            )

            self._state.mode = (
                TimelineSelectionMode.MULTI
                if len(
                    self._state
                    .selected_track_ids
                )
                > 1
                else TimelineSelectionMode.SINGLE
            )
        else:
            self._state.selected_track_ids = [
                track_id
            ]
            self._state.selected_clip_ids = []
            self._state.mode = (
                TimelineSelectionMode.SINGLE
            )

        self._state.active_track_id = (
            track_id
        )

        if not additive:
            self._state.active_clip_id = None

        self._state.focus = (
            TimelineSelectionFocus.TRACK
        )

        self._touch()

        event = self._emit(
            TimelineSelectionEventType
            .TRACK_SELECTED,
            metadata={
                "track_id": track_id,
                "additive": additive,
            },
        )

        return self._success(event)

    def select_clip(
        self,
        clip_id: str,
        *,
        additive: bool = False,
        move_cursor: bool = False,
    ) -> TimelineSelectionResult:
        error = self.validator.validate_clip(
            self.catalog,
            clip_id,
        )

        if error:
            return self._fail(error)

        clip = self.catalog.get_clip(
            clip_id
        )

        if clip is None:
            return self._fail(
                "Timeline clip could not be loaded."
            )

        if additive:
            selected = list(
                self._state.selected_clip_ids
            )

            if clip_id in selected:
                selected.remove(clip_id)
            else:
                selected.append(clip_id)

            self._state.selected_clip_ids = (
                self._unique(selected)
            )

            selected_count = len(
                self._state.selected_clip_ids
            )

            if selected_count == 0:
                self._state.mode = (
                    TimelineSelectionMode.NONE
                )
            elif selected_count == 1:
                self._state.mode = (
                    TimelineSelectionMode.SINGLE
                )
            else:
                self._state.mode = (
                    TimelineSelectionMode.MULTI
                )
        else:
            self._state.selected_clip_ids = [
                clip_id
            ]

            self._state.selected_track_ids = [
                clip.track_id
            ]

            self._state.mode = (
                TimelineSelectionMode.SINGLE
            )

        self._state.active_clip_id = (
            clip_id
        )

        self._state.active_track_id = (
            clip.track_id
        )

        self._state.focus = (
            TimelineSelectionFocus.CLIP
        )

        if move_cursor:
            self._set_cursor_value(
                clip.start_time
            )

        self._touch()

        event = self._emit(
            TimelineSelectionEventType
            .CLIP_SELECTED,
            metadata={
                "clip_id": clip_id,
                "track_id": clip.track_id,
                "additive": additive,
                "cursor_moved": (
                    move_cursor
                ),
            },
        )

        return self._success(event)

    def select_multiple(
        self,
        *,
        track_ids: list[str] | None = None,
        clip_ids: list[str] | None = None,
        replace: bool = True,
    ) -> TimelineSelectionResult:
        normalized_track_ids = (
            self._unique(track_ids or [])
        )

        normalized_clip_ids = (
            self._unique(clip_ids or [])
        )

        track_error = (
            self.validator.validate_track_ids(
                self.catalog,
                normalized_track_ids,
            )
        )

        if track_error:
            return self._fail(track_error)

        clip_error = (
            self.validator.validate_clip_ids(
                self.catalog,
                normalized_clip_ids,
            )
        )

        if clip_error:
            return self._fail(clip_error)

        if replace:
            selected_tracks = (
                normalized_track_ids
            )
            selected_clips = (
                normalized_clip_ids
            )
        else:
            selected_tracks = self._unique(
                [
                    *self._state
                    .selected_track_ids,
                    *normalized_track_ids,
                ]
            )

            selected_clips = self._unique(
                [
                    *self._state
                    .selected_clip_ids,
                    *normalized_clip_ids,
                ]
            )

        for clip_id in selected_clips:
            clip = self.catalog.get_clip(
                clip_id
            )

            if (
                clip is not None
                and clip.track_id
                not in selected_tracks
            ):
                selected_tracks.append(
                    clip.track_id
                )

        self._state.selected_track_ids = (
            selected_tracks
        )

        self._state.selected_clip_ids = (
            selected_clips
        )

        total_selected = (
            len(selected_tracks)
            + len(selected_clips)
        )

        if total_selected == 0:
            self._state.mode = (
                TimelineSelectionMode.NONE
            )
        elif total_selected == 1:
            self._state.mode = (
                TimelineSelectionMode.SINGLE
            )
        else:
            self._state.mode = (
                TimelineSelectionMode.MULTI
            )

        self._state.active_track_id = (
            selected_tracks[-1]
            if selected_tracks
            else None
        )

        self._state.active_clip_id = (
            selected_clips[-1]
            if selected_clips
            else None
        )

        self._state.focus = (
            TimelineSelectionFocus.CLIP
            if selected_clips
            else TimelineSelectionFocus.TRACK
            if selected_tracks
            else TimelineSelectionFocus.TIMELINE
        )

        self._touch()

        event = self._emit(
            TimelineSelectionEventType
            .MULTI_SELECTION_CHANGED,
            metadata={
                "track_ids": (
                    selected_tracks
                ),
                "clip_ids": (
                    selected_clips
                ),
                "replace": replace,
            },
        )

        return self._success(event)

    def hover_track(
        self,
        track_id: str | None,
    ) -> TimelineSelectionResult:
        if track_id is None:
            self._state.hovered_track_id = None
            self._touch()

            event = self._emit(
                TimelineSelectionEventType
                .HOVER_CLEARED,
            )

            return self._success(event)

        error = self.validator.validate_track(
            self.catalog,
            track_id,
        )

        if error:
            return self._fail(error)

        self._state.hovered_track_id = (
            track_id
        )

        self._touch()

        event = self._emit(
            TimelineSelectionEventType
            .TRACK_HOVERED,
            metadata={
                "track_id": track_id,
            },
        )

        return self._success(event)

    def hover_clip(
        self,
        clip_id: str | None,
    ) -> TimelineSelectionResult:
        if clip_id is None:
            self._state.hovered_clip_id = None
            self._touch()

            event = self._emit(
                TimelineSelectionEventType
                .HOVER_CLEARED,
            )

            return self._success(event)

        error = self.validator.validate_clip(
            self.catalog,
            clip_id,
        )

        if error:
            return self._fail(error)

        clip = self.catalog.get_clip(
            clip_id
        )

        self._state.hovered_clip_id = (
            clip_id
        )

        self._state.hovered_track_id = (
            clip.track_id
            if clip
            else None
        )

        self._touch()

        event = self._emit(
            TimelineSelectionEventType
            .CLIP_HOVERED,
            metadata={
                "clip_id": clip_id,
                "track_id": (
                    clip.track_id
                    if clip
                    else None
                ),
            },
        )

        return self._success(event)

    def clear_hover(
        self,
    ) -> TimelineSelectionResult:
        self._state.hovered_track_id = None
        self._state.hovered_clip_id = None

        self._touch()

        event = self._emit(
            TimelineSelectionEventType
            .HOVER_CLEARED,
        )

        return self._success(event)

    def set_cursor(
        self,
        value: float,
        *,
        select_clips_at_cursor: bool = False,
    ) -> TimelineSelectionResult:
        error = self.validator.validate_cursor(
            self.catalog,
            value,
        )

        if error:
            return self._fail(error)

        self._set_cursor_value(
            float(value)
        )

        selected_clip_ids: list[str] = []

        if select_clips_at_cursor:
            clips = self.catalog.clips_at_time(
                self._state.cursor_time
            )

            selected_clip_ids = [
                item.clip_id
                for item in clips
            ]

            selected_track_ids = self._unique(
                [
                    item.track_id
                    for item in clips
                ]
            )

            self._state.selected_clip_ids = (
                selected_clip_ids
            )

            self._state.selected_track_ids = (
                selected_track_ids
            )

            if len(selected_clip_ids) > 1:
                self._state.mode = (
                    TimelineSelectionMode.MULTI
                )
            elif len(selected_clip_ids) == 1:
                self._state.mode = (
                    TimelineSelectionMode.SINGLE
                )

        self._touch()

        event = self._emit(
            TimelineSelectionEventType
            .CURSOR_CHANGED,
            metadata={
                "cursor_time": (
                    self._state.cursor_time
                ),
                "cursor_frame": (
                    self._state.cursor_frame
                ),
                "selected_clip_ids": (
                    selected_clip_ids
                ),
            },
        )

        return self._success(event)

    def move_cursor(
        self,
        delta_seconds: float,
    ) -> TimelineSelectionResult:
        target = min(
            self.catalog.duration,
            max(
                0.0,
                self._state.cursor_time
                + float(delta_seconds),
            ),
        )

        return self.set_cursor(target)

    def step_cursor_frames(
        self,
        frame_count: int,
    ) -> TimelineSelectionResult:
        delta = (
            int(frame_count)
            / self.catalog.fps
        )

        return self.move_cursor(delta)

    def set_range(
        self,
        start_time: float,
        end_time: float,
    ) -> TimelineSelectionResult:
        time_range = TimelineTimeRange(
            start_time=start_time,
            end_time=end_time,
        )

        error = self.validator.validate_range(
            self.catalog,
            time_range,
        )

        if error:
            return self._fail(error)

        self._state.selected_range = (
            time_range
        )

        self._state.mode = (
            TimelineSelectionMode.RANGE
        )

        self._state.focus = (
            TimelineSelectionFocus.TIMELINE
        )

        self._touch()

        event = self._emit(
            TimelineSelectionEventType
            .RANGE_CHANGED,
            metadata=time_range.to_dict(),
        )

        return self._success(event)

    def clear_range(
        self,
    ) -> TimelineSelectionResult:
        self._state.selected_range = None

        self._recalculate_mode()

        self._touch()

        event = self._emit(
            TimelineSelectionEventType
            .RANGE_CLEARED,
        )

        return self._success(event)

    def set_focus(
        self,
        focus: (
            TimelineSelectionFocus | str
        ),
    ) -> TimelineSelectionResult:
        try:
            normalized_focus = (
                TimelineSelectionFocus(
                    focus
                )
            )
        except ValueError:
            return self._fail(
                f"Unsupported selection focus: {focus}"
            )

        self._state.focus = (
            normalized_focus
        )

        self._touch()

        event = self._emit(
            TimelineSelectionEventType
            .FOCUS_CHANGED,
            metadata={
                "focus": (
                    normalized_focus.value
                ),
            },
        )

        return self._success(event)

    def clear_selection(
        self,
        *,
        preserve_cursor: bool = True,
        preserve_hover: bool = True,
    ) -> TimelineSelectionResult:
        self._state.selected_track_ids = []
        self._state.selected_clip_ids = []

        self._state.active_track_id = None
        self._state.active_clip_id = None
        self._state.selected_range = None

        self._state.mode = (
            TimelineSelectionMode.NONE
        )

        self._state.focus = (
            TimelineSelectionFocus.TIMELINE
        )

        if not preserve_cursor:
            self._set_cursor_value(0.0)

        if not preserve_hover:
            self._state.hovered_track_id = None
            self._state.hovered_clip_id = None

        self._touch()

        event = self._emit(
            TimelineSelectionEventType
            .SELECTION_CLEARED,
            metadata={
                "preserve_cursor": (
                    preserve_cursor
                ),
                "preserve_hover": (
                    preserve_hover
                ),
            },
        )

        return self._success(event)

    def reset(
        self,
    ) -> TimelineSelectionResult:
        created_at = self._state.created_at

        self._state = deepcopy(
            self._initial_state
        )

        self._state.created_at = created_at
        self._state.revision += 1
        self._state.updated_at = (
            utc_now_iso()
        )

        event = self._emit(
            TimelineSelectionEventType
            .SESSION_RESET,
        )

        return self._success(event)

    def selected_tracks(
        self,
    ) -> list[Any]:
        return [
            self.catalog.get_track(
                track_id
            )
            for track_id
            in self._state.selected_track_ids
            if self.catalog.get_track(
                track_id
            )
            is not None
        ]

    def selected_clips(
        self,
    ) -> list[Any]:
        return [
            self.catalog.get_clip(
                clip_id
            )
            for clip_id
            in self._state.selected_clip_ids
            if self.catalog.get_clip(
                clip_id
            )
            is not None
        ]

    def clear_events(self) -> None:
        self._events.clear()

    def to_dict(self) -> dict[str, Any]:
        return {
            "catalog": (
                self.catalog.to_dict()
            ),
            "state": self._state.to_dict(),
            "selected_tracks": [
                item.to_dict()
                for item
                in self.selected_tracks()
            ],
            "selected_clips": [
                item.to_dict()
                for item
                in self.selected_clips()
            ],
            "events": [
                item.to_dict()
                for item in self._events
            ],
            "metadata": {
                "runtime": (
                    "TimelineSelectionRuntime"
                ),
                "event_count": len(
                    self._events
                ),
            },
        }

    def _set_cursor_value(
        self,
        value: float,
    ) -> None:
        cursor_time = min(
            self.catalog.duration,
            max(0.0, float(value)),
        )

        self._state.cursor_time = (
            cursor_time
        )

        self._state.cursor_frame = int(
            round(
                cursor_time
                * self.catalog.fps
            )
        )

    def _recalculate_mode(
        self,
    ) -> None:
        if self._state.selected_range:
            self._state.mode = (
                TimelineSelectionMode.RANGE
            )
            return

        count = (
            len(self._state.selected_track_ids)
            + len(self._state.selected_clip_ids)
        )

        if count == 0:
            self._state.mode = (
                TimelineSelectionMode.NONE
            )
        elif count == 1:
            self._state.mode = (
                TimelineSelectionMode.SINGLE
            )
        else:
            self._state.mode = (
                TimelineSelectionMode.MULTI
            )

    def _unique(
        self,
        values: list[str],
    ) -> list[str]:
        return list(
            dict.fromkeys(
                str(item)
                for item in values
                if item
            )
        )

    def _touch(self) -> None:
        self._state.revision += 1
        self._state.updated_at = (
            utc_now_iso()
        )

    def _emit(
        self,
        event_type: TimelineSelectionEventType,
        *,
        metadata: dict[str, Any]
        | None = None,
    ) -> TimelineSelectionEvent:
        event = TimelineSelectionEvent(
            event_type=event_type,
            production_id=(
                self.catalog.production_id
            ),
            state_revision=(
                self._state.revision
            ),
            metadata=dict(
                metadata or {}
            ),
        )

        self._events.append(event)

        if self.event_callback:
            self.event_callback(event)

        return event

    def _success(
        self,
        event: TimelineSelectionEvent
        | None = None,
    ) -> TimelineSelectionResult:
        return TimelineSelectionResult(
            success=True,
            state=self.state,
            event=event,
            error=None,
        )

    def _fail(
        self,
        message: str,
    ) -> TimelineSelectionResult:
        event = self._emit(
            TimelineSelectionEventType
            .VALIDATION_FAILED,
            metadata={
                "error": message,
            },
        )

        return TimelineSelectionResult(
            success=False,
            state=self.state,
            event=event,
            error=message,
        )