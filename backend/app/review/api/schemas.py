from __future__ import annotations

from copy import deepcopy
from typing import Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.review.api.contracts import (
    REVIEW_AI_COMMAND_API_CONTRACT_VERSION,
    REVIEW_AI_SUGGESTION_API_CONTRACT_VERSION,
    REVIEW_CLIPBOARD_API_CONTRACT_VERSION,
    REVIEW_TIMELINE_COMMAND_API_CONTRACT_VERSION,
    REVIEW_WORKSPACE_API_CONTRACT_VERSION,
    ReviewAICommandAPIOperation,
    ReviewClipboardOperation,
    ReviewAISuggestionAPIOperation,
    ReviewTimelineCommandOperation,
    ReviewWorkspaceAPIErrorCode,
    ReviewWorkspaceAPIOperation,
)


class ReviewWorkspaceAPISchema(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class OpenReviewWorkspaceRequest(
    ReviewWorkspaceAPISchema
):
    force_refresh: bool = False
    replace_existing: bool = False

    @model_validator(mode="after")
    def validate_refresh_policy(
        self,
    ) -> OpenReviewWorkspaceRequest:
        if (
            self.force_refresh
            and not self.replace_existing
        ):
            raise ValueError(
                "force_refresh requires "
                "replace_existing."
            )

        return self


class ReviewWorkspaceSessionQuery(
    ReviewWorkspaceAPISchema
):
    session_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=128,
    )


class ReviewWorkspaceSessionCommandRequest(
    ReviewWorkspaceAPISchema
):
    session_id: str = Field(
        min_length=1,
        max_length=128,
    )


class ResetReviewWorkspaceRequest(
    ReviewWorkspaceSessionCommandRequest
):
    pass


class CloseReviewWorkspaceRequest(
    ReviewWorkspaceSessionCommandRequest
):
    pass


class SelectTimelineClipRequest(
    ReviewWorkspaceSessionCommandRequest
):
    clip_id: str = Field(
        min_length=1,
        max_length=256,
    )
    additive: bool = False
    move_cursor: bool = False


class ReviewTimelineCommandRequest(
    ReviewWorkspaceSessionCommandRequest
):
    expected_revision: int | None = Field(
        default=None,
        ge=1,
    )


class MoveTimelineClipRequest(
    ReviewTimelineCommandRequest
):
    clip_id: str = Field(
        min_length=1,
        max_length=256,
    )
    new_start_time: float = Field(
        ge=0.0,
    )
    target_track_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=256,
    )


class MultiTimelineClipRequest(ReviewTimelineCommandRequest):
    clip_ids: list[str] = Field(min_length=2, max_length=256)

    @field_validator("clip_ids")
    @classmethod
    def normalize_clip_ids(cls, value: list[str]) -> list[str]:
        normalized: list[str] = []
        for raw_id in value:
            clip_id = str(raw_id).strip()
            if not clip_id:
                raise ValueError("clip_ids must not contain empty values.")
            if len(clip_id) > 256:
                raise ValueError("clip_ids values must be at most 256 characters.")
            if clip_id not in normalized:
                normalized.append(clip_id)
        if len(normalized) < 2:
            raise ValueError("clip_ids must contain at least two unique clips.")
        return normalized


class MoveTimelineClipsRequest(MultiTimelineClipRequest):
    delta_time: float

    @field_validator("delta_time")
    @classmethod
    def validate_delta_time(cls, value: float) -> float:
        if float(value) == 0:
            raise ValueError("delta_time must not be zero.")
        return float(value)


class DuplicateTimelineClipsRequest(MultiTimelineClipRequest):
    time_offset: float | None = Field(default=None, gt=0.0)


class DeleteTimelineClipsRequest(MultiTimelineClipRequest):
    pass


class TrimTimelineClipStartRequest(
    ReviewTimelineCommandRequest
):
    clip_id: str = Field(
        min_length=1,
        max_length=256,
    )
    new_start_time: float = Field(
        ge=0.0,
    )


class TrimTimelineClipEndRequest(
    ReviewTimelineCommandRequest
):
    clip_id: str = Field(
        min_length=1,
        max_length=256,
    )
    new_end_time: float = Field(
        gt=0.0,
    )


class SplitTimelineClipRequest(
    ReviewTimelineCommandRequest
):
    clip_id: str = Field(
        min_length=1,
        max_length=256,
    )
    split_time: float = Field(
        gt=0.0,
    )
    right_clip_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=256,
    )


class DuplicateTimelineClipRequest(
    ReviewTimelineCommandRequest
):
    clip_id: str = Field(
        min_length=1,
        max_length=256,
    )
    new_clip_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=256,
    )
    new_start_time: float | None = Field(
        default=None,
        ge=0.0,
    )
    target_track_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=256,
    )


class DeleteTimelineClipRequest(
    ReviewTimelineCommandRequest
):
    clip_id: str = Field(
        min_length=1,
        max_length=256,
    )
    close_gap: bool = False


class CloseTimelineGapRequest(
    ReviewTimelineCommandRequest
):
    track_id: str = Field(
        min_length=1,
        max_length=256,
    )
    gap_start: float = Field(
        ge=0.0,
    )
    gap_end: float = Field(
        gt=0.0,
    )

    @model_validator(mode="after")
    def validate_gap_range(
        self,
    ) -> CloseTimelineGapRequest:
        if self.gap_end <= self.gap_start:
            raise ValueError(
                "gap_end must be greater than "
                "gap_start."
            )

        return self


class UndoTimelineCommandRequest(
    ReviewTimelineCommandRequest
):
    pass


class RedoTimelineCommandRequest(
    ReviewTimelineCommandRequest
):
    pass


class ReviewClipboardCommandRequest(
    ReviewWorkspaceSessionCommandRequest
):
    expected_revision: int | None = Field(
        default=None,
        ge=1,
    )


class CopyTimelineClipsRequest(
    ReviewClipboardCommandRequest
):
    clip_ids: list[str] = Field(
        min_length=1,
        max_length=100,
    )

    @field_validator("clip_ids", mode="before")
    @classmethod
    def normalize_clip_ids(
        cls,
        value: Any,
    ) -> Any:
        if not isinstance(value, (list, tuple)):
            return value

        normalized = list(
            dict.fromkeys(
                str(item).strip()
                for item in value
                if str(item).strip()
            )
        )
        if not normalized:
            raise ValueError(
                "clip_ids must contain at least "
                "one clip_id."
            )
        return normalized


class CutTimelineClipsRequest(
    CopyTimelineClipsRequest
):
    pass


class PasteTimelineClipsRequest(
    ReviewClipboardCommandRequest
):
    at_time: float = Field(ge=0.0)
    target_track_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=256,
    )
    track_mapping: dict[str, str] | None = Field(
        default=None,
        max_length=100,
    )

    @field_validator(
        "track_mapping",
        mode="before",
    )
    @classmethod
    def normalize_track_mapping(
        cls,
        value: Any,
    ) -> Any:
        if value is None or not isinstance(value, dict):
            return value

        normalized: dict[str, str] = {}
        for source, target in value.items():
            source_id = str(source).strip()
            target_id = str(target).strip()
            if not source_id or not target_id:
                raise ValueError(
                    "track_mapping keys and values "
                    "cannot be empty."
                )
            normalized[source_id] = target_id
        return normalized


class RestoreTimelineClipboardHistoryRequest(
    ReviewClipboardCommandRequest
):
    entry_id: str = Field(
        min_length=1,
        max_length=128,
    )


class ClearTimelineClipboardRequest(
    ReviewClipboardCommandRequest
):
    pass


class ClearTimelineClipboardHistoryRequest(
    ReviewClipboardCommandRequest
):
    pass


class ReviewAISuggestionRequest(
    ReviewWorkspaceSessionCommandRequest
):
    expected_lifecycle_revision: int | None = Field(
        default=None,
        ge=1,
    )


class SelectAISuggestionRequest(
    ReviewAISuggestionRequest
):
    suggestion_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=256,
    )


class ApplyAISuggestionRequest(
    ReviewAISuggestionRequest
):
    suggestion_id: str = Field(
        min_length=1,
        max_length=256,
    )
    expected_timeline_revision: int | None = Field(
        default=None,
        ge=1,
    )


class DismissAISuggestionRequest(
    ReviewAISuggestionRequest
):
    suggestion_id: str = Field(
        min_length=1,
        max_length=256,
    )


class RegenerateAISuggestionsRequest(
    ReviewAISuggestionRequest
):
    pass


class ReviewWorkspaceSuccessResponse(
    ReviewWorkspaceAPISchema
):
    contract_version: Literal["16.2.3"] = (
        REVIEW_WORKSPACE_API_CONTRACT_VERSION
    )

    success: Literal[True] = True
    operation: ReviewWorkspaceAPIOperation

    production_id: str = Field(
        min_length=1,
    )
    session_id: str = Field(
        min_length=1,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


class ReviewWorkspaceSessionResponse(
    ReviewWorkspaceSuccessResponse
):
    session: dict[str, Any]
    snapshot: dict[str, Any]


class ReviewWorkspaceSnapshotResponse(
    ReviewWorkspaceSuccessResponse
):
    snapshot: dict[str, Any]

    @field_validator(
        "snapshot",
        "metadata",
        mode="before",
    )
    @classmethod
    def clone_snapshot_payload(
        cls,
        value: Any,
    ) -> Any:
        return deepcopy(value)


class ReviewWorkspaceResetResponse(
    ReviewWorkspaceSnapshotResponse
):
    operation: Literal[
        ReviewWorkspaceAPIOperation.RESET_SESSION
    ] = ReviewWorkspaceAPIOperation.RESET_SESSION


class ReviewWorkspaceCloseResponse(
    ReviewWorkspaceSuccessResponse
):
    operation: Literal[
        ReviewWorkspaceAPIOperation.CLOSE_SESSION
    ] = ReviewWorkspaceAPIOperation.CLOSE_SESSION

    state: dict[str, Any]
    event: dict[str, Any] | None = None


class ReviewTimelineCommandResponse(
    ReviewWorkspaceAPISchema
):
    contract_version: Literal["16.4.1"] = (
        REVIEW_TIMELINE_COMMAND_API_CONTRACT_VERSION
    )

    success: Literal[True] = True
    operation: ReviewTimelineCommandOperation

    production_id: str = Field(
        min_length=1,
    )
    session_id: str = Field(
        min_length=1,
        max_length=128,
    )

    snapshot: dict[str, Any]
    command: dict[str, Any] | None = None
    event: dict[str, Any] | None = None
    history: dict[str, Any]

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    @field_validator(
        "snapshot",
        "command",
        "event",
        "history",
        "metadata",
        mode="before",
    )
    @classmethod
    def clone_response_payload(
        cls,
        value: Any,
    ) -> Any:
        return deepcopy(value)


class ReviewClipboardCommandResponse(
    ReviewWorkspaceAPISchema
):
    contract_version: Literal["16.4.8"] = (
        REVIEW_CLIPBOARD_API_CONTRACT_VERSION
    )

    success: Literal[True] = True
    operation: ReviewClipboardOperation

    production_id: str = Field(
        min_length=1,
    )
    session_id: str = Field(
        min_length=1,
        max_length=128,
    )

    previous_revision: int = Field(ge=1)
    current_revision: int = Field(ge=1)

    snapshot: dict[str, Any]
    clipboard: dict[str, Any]
    timeline_history: dict[str, Any] | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    @field_validator(
        "snapshot",
        "clipboard",
        "timeline_history",
        "metadata",
        mode="before",
    )
    @classmethod
    def clone_clipboard_response_payload(
        cls,
        value: Any,
    ) -> Any:
        return deepcopy(value)


class ReviewAISuggestionResponse(
    ReviewWorkspaceAPISchema
):
    contract_version: Literal["16.6.4"] = (
        REVIEW_AI_SUGGESTION_API_CONTRACT_VERSION
    )
    success: Literal[True] = True
    operation: ReviewAISuggestionAPIOperation
    production_id: str = Field(min_length=1)
    session_id: str = Field(
        min_length=1,
        max_length=128,
    )
    timeline_revision: int = Field(ge=1)
    lifecycle_revision: int = Field(ge=1)
    workspace_snapshot: dict[str, Any]
    suggestion_snapshot: dict[str, Any]
    timeline_command_result: dict[str, Any] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator(
        "workspace_snapshot",
        "suggestion_snapshot",
        "timeline_command_result",
        "metadata",
        mode="before",
    )
    @classmethod
    def clone_ai_suggestion_response_payload(
        cls,
        value: Any,
    ) -> Any:
        return deepcopy(value)


class SubmitAICommandRequest(
    ReviewWorkspaceSessionCommandRequest
):
    command_text: str = Field(
        min_length=1,
        max_length=2000,
    )
    expected_timeline_revision: int | None = Field(
        default=None,
        ge=1,
    )
    client_request_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=128,
    )


class ReviewAICommandSubmissionResponse(
    ReviewWorkspaceAPISchema
):
    contract_version: Literal["16.6.8"] = (
        REVIEW_AI_COMMAND_API_CONTRACT_VERSION
    )
    success: Literal[True] = True
    operation: Literal[
        ReviewAICommandAPIOperation.SUBMIT
    ] = ReviewAICommandAPIOperation.SUBMIT
    production_id: str = Field(min_length=1)
    session_id: str = Field(min_length=1, max_length=128)
    timeline_revision: int = Field(ge=1)
    submission: dict[str, Any]
    duplicate: bool = False
    timeline_mutated: Literal[False] = False

    @field_validator("submission", mode="before")
    @classmethod
    def clone_command_submission(cls, value: Any) -> Any:
        return deepcopy(value)


class ReviewWorkspaceAPIErrorDetail(
    ReviewWorkspaceAPISchema
):
    code: ReviewWorkspaceAPIErrorCode
    message: str = Field(
        min_length=1,
    )

    technical_message: str | None = None
    production_id: str | None = None
    session_id: str | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )


class ReviewWorkspaceErrorResponse(
    ReviewWorkspaceAPISchema
):
    contract_version: Literal["16.2.3"] = (
        REVIEW_WORKSPACE_API_CONTRACT_VERSION
    )

    success: Literal[False] = False
    error: ReviewWorkspaceAPIErrorDetail
