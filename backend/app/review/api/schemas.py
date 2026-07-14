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
    REVIEW_TIMELINE_COMMAND_API_CONTRACT_VERSION,
    REVIEW_WORKSPACE_API_CONTRACT_VERSION,
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


class ReviewWorkspaceSuccessResponse(
    ReviewWorkspaceAPISchema
):
    contract_version: Literal["16.2.3"] = (
        REVIEW_WORKSPACE_API_CONTRACT_VERSION
    )

    success: Literal[True] = True
    operation: ReviewWorkspaceAPIOperation

    production_id: str = Field(
        min_length=1
    )
    session_id: str = Field(
        min_length=1
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
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
        default_factory=dict
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


class ReviewWorkspaceAPIErrorDetail(
    ReviewWorkspaceAPISchema
):
    code: ReviewWorkspaceAPIErrorCode
    message: str = Field(
        min_length=1
    )

    technical_message: str | None = None
    production_id: str | None = None
    session_id: str | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class ReviewWorkspaceErrorResponse(
    ReviewWorkspaceAPISchema
):
    contract_version: Literal["16.2.3"] = (
        REVIEW_WORKSPACE_API_CONTRACT_VERSION
    )

    success: Literal[False] = False
    error: ReviewWorkspaceAPIErrorDetail