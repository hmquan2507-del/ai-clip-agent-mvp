from __future__ import annotations

from typing import Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from app.review.api.contracts import (
    REVIEW_WORKSPACE_API_CONTRACT_VERSION,
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