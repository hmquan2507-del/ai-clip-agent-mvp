from __future__ import annotations

from enum import StrEnum


class TimelineClipboardAction(StrEnum):
    COPY = "copy"
    CUT = "cut"
    PASTE = "paste"
    CLEAR = "clear"
    RESTORE = "restore"


class TimelineClipboardStatus(StrEnum):
    EMPTY = "empty"
    READY = "ready"
    FAILED = "failed"


class TimelineClipboardItemType(StrEnum):
    CLIP = "clip"


class TimelineClipboardEventType(StrEnum):
    CLIP_COPIED = "clip_copied"
    CLIPS_COPIED = "clips_copied"

    CLIP_CUT = "clip_cut"
    CLIPS_CUT = "clips_cut"

    CLIP_PASTED = "clip_pasted"
    CLIPS_PASTED = "clips_pasted"

    HISTORY_RESTORED = "history_restored"
    HISTORY_CLEARED = "history_cleared"

    CLIPBOARD_CLEARED = "clipboard_cleared"

    COPY_FAILED = "copy_failed"
    CUT_FAILED = "cut_failed"
    PASTE_FAILED = "paste_failed"