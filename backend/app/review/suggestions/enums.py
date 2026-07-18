from __future__ import annotations

from enum import StrEnum


class AISuggestionKind(StrEnum):
    HOOK = "hook"
    PACING = "pacing"
    BROLL = "broll"
    SUBTITLE = "subtitle"
    MUSIC = "music"
    SOUND_EFFECT = "sound_effect"
    TRANSITION = "transition"
    GENERIC = "generic"


class AISuggestionStatus(StrEnum):
    PROPOSED = "proposed"
    APPLIED = "applied"
    DISMISSED = "dismissed"
    STALE = "stale"


class AISuggestionTargetType(StrEnum):
    TIMELINE = "timeline"
    TRACK = "track"
    CLIP = "clip"
    RANGE = "range"
