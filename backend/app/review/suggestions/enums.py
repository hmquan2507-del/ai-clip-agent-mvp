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


class AISuggestionStoreChangeReason(StrEnum):
    SELECT = "select"
    APPLY = "apply"
    DISMISS = "dismiss"
    REGENERATE = "regenerate"
    SYNCHRONIZE = "synchronize"
    RESET = "reset"
    REPLACE = "replace"


class AISuggestionLifecycleEventType(StrEnum):
    SUGGESTION_SELECTED = "suggestion_selected"
    SUGGESTION_APPLIED = "suggestion_applied"
    SUGGESTION_DISMISSED = "suggestion_dismissed"
    SUGGESTIONS_REGENERATED = (
        "suggestions_regenerated"
    )
    TIMELINE_SYNCHRONIZED = (
        "timeline_synchronized"
    )
    LIFECYCLE_RESET = "lifecycle_reset"
