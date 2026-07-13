from __future__ import annotations

from enum import StrEnum


class PreviewPlaybackStatus(StrEnum):
    IDLE = "idle"
    READY = "ready"
    PLAYING = "playing"
    PAUSED = "paused"
    ENDED = "ended"
    ERROR = "error"


class PreviewSessionEventType(StrEnum):
    SESSION_CREATED = "session_created"
    SESSION_READY = "session_ready"

    PLAYBACK_STARTED = "playback_started"
    PLAYBACK_PAUSED = "playback_paused"
    PLAYBACK_ENDED = "playback_ended"

    POSITION_CHANGED = "position_changed"
    FRAME_STEPPED = "frame_stepped"

    VOLUME_CHANGED = "volume_changed"
    MUTE_CHANGED = "mute_changed"
    PLAYBACK_RATE_CHANGED = "playback_rate_changed"
    ZOOM_CHANGED = "zoom_changed"
    LOOP_CHANGED = "loop_changed"

    SESSION_RESET = "session_reset"
    SESSION_ERROR = "session_error"