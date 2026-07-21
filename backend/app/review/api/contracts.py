from __future__ import annotations

from enum import Enum


REVIEW_WORKSPACE_API_CONTRACT_VERSION = "16.2.3"

REVIEW_TIMELINE_COMMAND_API_CONTRACT_VERSION = (
    "16.4.1"
)

REVIEW_CLIPBOARD_API_CONTRACT_VERSION = (
    "16.4.8"
)

REVIEW_AI_SUGGESTION_API_CONTRACT_VERSION = (
    "16.6.4"
)

REVIEW_AI_COMMAND_API_CONTRACT_VERSION = "16.6.8"
REVIEW_MULTI_SELECT_API_CONTRACT_VERSION = "16.7.7"


class ReviewWorkspaceAPIOperation(str, Enum):
    OPEN_SESSION = "open_session"
    GET_SESSION = "get_session"
    GET_SNAPSHOT = "get_snapshot"
    RESET_SESSION = "reset_session"
    CLOSE_SESSION = "close_session"

    SELECT_CLIP = "select_clip"


class ReviewTimelineCommandOperation(str, Enum):
    MOVE_CLIP = "move_clip"
    MOVE_CLIPS = "move_clips"
    TRIM_CLIP_START = "trim_clip_start"
    TRIM_CLIP_END = "trim_clip_end"
    SPLIT_CLIP = "split_clip"
    DUPLICATE_CLIP = "duplicate_clip"
    DUPLICATE_CLIPS = "duplicate_clips"
    DELETE_CLIP = "delete_clip"
    DELETE_CLIPS = "delete_clips"
    CLOSE_GAP = "close_gap"
    UNDO = "undo"
    REDO = "redo"


class ReviewClipboardOperation(str, Enum):
    COPY = "copy"
    CUT = "cut"
    PASTE = "paste"
    RESTORE_HISTORY = "restore_history"
    CLEAR_CONTENT = "clear_content"
    CLEAR_HISTORY = "clear_history"


class ReviewAISuggestionAPIOperation(str, Enum):
    GET = "get_suggestions"
    SELECT = "select_suggestion"
    APPLY = "apply_suggestion"
    DISMISS = "dismiss_suggestion"
    REGENERATE = "regenerate_suggestions"


class ReviewAICommandAPIOperation(str, Enum):
    SUBMIT = "submit_command"


class ReviewWorkspaceAPIErrorCode(str, Enum):
    PRODUCTION_NOT_FOUND = (
        "production_not_found"
    )
    WORKSPACE_LOAD_FAILED = (
        "workspace_load_failed"
    )
    SESSION_NOT_FOUND = (
        "review_session_not_found"
    )
    SESSION_CONFLICT = (
        "review_session_conflict"
    )
    SESSION_OPERATION_FAILED = (
        "review_session_operation_failed"
    )
    CLIPBOARD_COMMAND_FAILED = (
        "review_clipboard_command_failed"
    )
    AI_SUGGESTION_OPERATION_FAILED = (
        "review_ai_suggestion_operation_failed"
    )
    AI_SUGGESTION_REVISION_CONFLICT = (
        "review_ai_suggestion_revision_conflict"
    )
    AI_COMMAND_SUBMISSION_FAILED = (
        "review_ai_command_submission_failed"
    )
    AI_COMMAND_REVISION_CONFLICT = (
        "review_ai_command_revision_conflict"
    )
    VALIDATION_ERROR = (
        "review_request_validation_failed"
    )
    INTERNAL_ERROR = (
        "review_workspace_internal_error"
    )
