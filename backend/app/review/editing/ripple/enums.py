from __future__ import annotations

from enum import StrEnum


class RippleEditPolicy(StrEnum):
    DISABLED = "disabled"
    TRACK = "track"
    ALL_UNLOCKED_TRACKS = "all_unlocked_tracks"


class RippleEditOperation(StrEnum):
    DELETE = "ripple_delete"
    CLOSE_RANGE = "ripple_close_range"
