from __future__ import annotations

from enum import StrEnum


class EditableTrackType(StrEnum):
    VIDEO_PRIMARY = "video_primary"
    VIDEO_OVERLAY = "video_overlay"
    BROLL = "broll"
    SUBTITLE = "subtitle"
    MUSIC = "music"
    SOUND_EFFECT = "sound_effect"
    VOICE = "voice"
    AUDIO = "audio"
    EFFECT = "effect"
    UNKNOWN = "unknown"


class EditableClipType(StrEnum):
    VIDEO = "video"
    BROLL = "broll"
    SUBTITLE = "subtitle"
    MUSIC = "music"
    SOUND_EFFECT = "sound_effect"
    VOICE = "voice"
    AUDIO = "audio"
    EFFECT = "effect"
    UNKNOWN = "unknown"


class TimelineDirtyStatus(StrEnum):
    CLEAN = "clean"
    DIRTY = "dirty"
    SAVING = "saving"
    SAVED = "saved"
    SAVE_FAILED = "save_failed"


class TimelineOverlapPolicy(StrEnum):
    FORBID = "forbid"
    ALLOW = "allow"


class TimelineEditingOperationType(StrEnum):
    MOVE_CLIP = "move_clip"
    TRIM_CLIP_START = "trim_clip_start"
    TRIM_CLIP_END = "trim_clip_end"
    INSERT_CLIP = "insert_clip"
    SPLIT_CLIP = "split_clip"
    DELETE_CLIP = "delete_clip"
    DUPLICATE_CLIP = "duplicate_clip"
    CLOSE_GAP = "close_gap"

    MOVE_CLIPS = "move_clips"
    DUPLICATE_CLIPS = "duplicate_clips"
    DELETE_CLIPS = "delete_clips"

    CUT_CLIPS = "cut_clips"
    PASTE_CLIPS = "paste_clips"

    RENAME_TRACK = "rename_track"
    LOCK_TRACK = "lock_track"
    MUTE_TRACK = "mute_track"
    HIDE_TRACK = "hide_track"

class TimelineEditingIssueCode(StrEnum):
    TIMELINE_NOT_FOUND = "timeline_not_found"

    TRACK_NOT_FOUND = "track_not_found"
    TRACK_LOCKED = "track_locked"
    TRACK_TYPE_MISMATCH = "track_type_mismatch"

    CLIP_NOT_FOUND = "clip_not_found"
    CLIP_ID_DUPLICATED = "clip_id_duplicated"
    CLIP_TRACK_MISMATCH = "clip_track_mismatch"

    INVALID_TIMELINE_RANGE = "invalid_timeline_range"
    INVALID_SOURCE_RANGE = "invalid_source_range"
    CLIP_TOO_SHORT = "clip_too_short"

    NEGATIVE_TIME = "negative_time"
    TIMELINE_DURATION_EXCEEDED = (
        "timeline_duration_exceeded"
    )
    SOURCE_DURATION_EXCEEDED = (
        "source_duration_exceeded"
    )

    CLIP_OVERLAP = "clip_overlap"
    INVALID_SPLIT_POINT = "invalid_split_point"
    INVALID_GAP = "invalid_gap"

