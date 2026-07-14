from __future__ import annotations

from typing import Any


class ReviewWorkspaceApplicationError(RuntimeError):
    code = "review_application_error"

    def __init__(
        self,
        message: str,
        *,
        production_id: str | None = None,
        session_id: str | None = None,
    ):
        super().__init__(message)
        self.production_id = production_id
        self.session_id = session_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": str(self),
            "production_id": self.production_id,
            "session_id": self.session_id,
        }


class ReviewRuntimeSessionNotFoundError(
    ReviewWorkspaceApplicationError
):
    code = "review_session_not_found"


class ReviewRuntimeSessionConflictError(
    ReviewWorkspaceApplicationError
):
    code = "review_session_conflict"


class ReviewRuntimeSessionOperationError(
    ReviewWorkspaceApplicationError
):
    code = "review_session_operation_failed"