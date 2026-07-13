from __future__ import annotations

from enum import StrEnum


class TimelineSelectionMode(StrEnum):
    NONE = "none"
    SINGLE = "single"
    MULTI = "multi"
    RANGE = "range"


class TimelineSelectionFocus(StrEnum):
    NONE = "none"
    TIMELINE = "timeline"
    TRACK = "track"
    CLIP = "clip"
    SUBTITLE = "subtitle"
    TRANSITION = "transition"
    EFFECT = "effect"
    ASSET = "asset"


class TimelineSelectionEventType(StrEnum):
    SESSION_CREATED = "session_created"

    TRACK_SELECTED = "track_selected"
    CLIP_SELECTED = "clip_selected"
    MULTI_SELECTION_CHANGED = "multi_selection_changed"

    TRACK_HOVERED = "track_hovered"
    CLIP_HOVERED = "clip_hovered"
    HOVER_CLEARED = "hover_cleared"

    CURSOR_CHANGED = "cursor_changed"
    RANGE_CHANGED = "range_changed"
    RANGE_CLEARED = "range_cleared"

    FOCUS_CHANGED = "focus_changed"
    SELECTION_CLEARED = "selection_cleared"
    SESSION_RESET = "session_reset"

    VALIDATION_FAILED = "validation_failed"