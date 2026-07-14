from __future__ import annotations

from enum import Enum


REVIEW_WORKSPACE_API_CONTRACT_VERSION = "16.2.3"


class ReviewWorkspaceAPIOperation(str, Enum):
    OPEN_SESSION = "open_session"
    GET_SESSION = "get_session"
    GET_SNAPSHOT = "get_snapshot"
    RESET_SESSION = "reset_session"
    CLOSE_SESSION = "close_session"


class ReviewWorkspaceAPIErrorCode(str, Enum):
    PRODUCTION_NOT_FOUND = "production_not_found"
    WORKSPACE_LOAD_FAILED = "workspace_load_failed"
    SESSION_NOT_FOUND = "review_session_not_found"
    SESSION_CONFLICT = "review_session_conflict"
    SESSION_OPERATION_FAILED = (
        "review_session_operation_failed"
    )
    VALIDATION_ERROR = (
        "review_request_validation_failed"
    )
    INTERNAL_ERROR = (
        "review_workspace_internal_error"
    )