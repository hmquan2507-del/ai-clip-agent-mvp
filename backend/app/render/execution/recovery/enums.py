from __future__ import annotations

from enum import StrEnum


class RenderFailureCategory(StrEnum):
    UNKNOWN = "unknown"

    CONTRACT_ERROR = "contract_error"
    INPUT_MISSING = "input_missing"
    INPUT_INVALID = "input_invalid"

    FFMPEG_NOT_INSTALLED = "ffmpeg_not_installed"
    FFMPEG_TIMEOUT = "ffmpeg_timeout"
    FFMPEG_PROCESS_ERROR = "ffmpeg_process_error"

    OUTPUT_MISSING = "output_missing"
    OUTPUT_INVALID = "output_invalid"

    DISK_FULL = "disk_full"
    PERMISSION_DENIED = "permission_denied"
    PROCESS_KILLED = "process_killed"

    ARTIFACT_STORE_ERROR = "artifact_store_error"


class RenderRetryDecision(StrEnum):
    RETRY = "retry"
    DO_NOT_RETRY = "do_not_retry"
    RETRY_AFTER_CLEANUP = "retry_after_cleanup"


class RenderCleanupMode(StrEnum):
    NONE = "none"
    PARTIAL = "partial"
    FULL = "full"