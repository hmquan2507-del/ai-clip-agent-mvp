from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.product import (
    ProductWorkspaceLoadError,
    ProductWorkspaceNotFoundError,
)
from app.review.api.contracts import (
    ReviewClipboardOperation,
    ReviewTimelineCommandOperation,
    ReviewWorkspaceAPIErrorCode,
    ReviewWorkspaceAPIOperation,
)
from app.review.api.schemas import (
    ReviewClipboardCommandResponse,
    ReviewTimelineCommandResponse,
    ReviewWorkspaceAPIErrorDetail,
    ReviewWorkspaceCloseResponse,
    ReviewWorkspaceErrorResponse,
    ReviewWorkspaceResetResponse,
    ReviewWorkspaceSessionResponse,
    ReviewWorkspaceSnapshotResponse,
)
from app.review.application import (
    ReviewClipboardCommandOperationError,
    ReviewClipboardCommandResult,
    ReviewRuntimeSessionConflictError,
    ReviewRuntimeSessionNotFoundError,
    ReviewRuntimeSessionOperationError,
    ReviewTimelineCommandResult,
    ReviewWorkspaceApplicationError,
)
from app.review.session import (
    ReviewRuntimeSession,
    ReviewRuntimeSessionResult,
    ReviewRuntimeSessionSnapshot,
)


class ReviewWorkspaceAPIMapper:
    @staticmethod
    def session_response(
        session: ReviewRuntimeSession,
        *,
        operation: ReviewWorkspaceAPIOperation = (
            ReviewWorkspaceAPIOperation
            .OPEN_SESSION
        ),
        metadata: dict[str, Any] | None = None,
    ) -> ReviewWorkspaceSessionResponse:
        snapshot = session.snapshot()

        return ReviewWorkspaceSessionResponse(
            operation=operation,
            production_id=(
                session.production_id
            ),
            session_id=session.session_id,
            session=session.state.to_dict(),
            snapshot=snapshot.to_dict(),
            metadata=deepcopy(
                metadata or {}
            ),
        )

    @staticmethod
    def snapshot_response(
        snapshot: ReviewRuntimeSessionSnapshot,
        *,
        operation: ReviewWorkspaceAPIOperation = (
            ReviewWorkspaceAPIOperation
            .GET_SNAPSHOT
        ),
        metadata: dict[str, Any] | None = None,
    ) -> ReviewWorkspaceSnapshotResponse:
        return ReviewWorkspaceSnapshotResponse(
            operation=operation,
            production_id=(
                snapshot.production_id
            ),
            session_id=snapshot.session_id,
            snapshot=snapshot.to_dict(),
            metadata=deepcopy(
                metadata or {}
            ),
        )

    @staticmethod
    def reset_response(
        snapshot: ReviewRuntimeSessionSnapshot,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> ReviewWorkspaceResetResponse:
        return ReviewWorkspaceResetResponse(
            production_id=(
                snapshot.production_id
            ),
            session_id=snapshot.session_id,
            snapshot=snapshot.to_dict(),
            metadata=deepcopy(
                metadata or {}
            ),
        )

    @staticmethod
    def close_response(
        result: ReviewRuntimeSessionResult,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> ReviewWorkspaceCloseResponse:
        if not result.success:
            raise ValueError(
                result.error
                or (
                    "Review runtime session "
                    "close failed."
                )
            )

        return ReviewWorkspaceCloseResponse(
            production_id=(
                result.state.production_id
            ),
            session_id=(
                result.state.session_id
            ),
            state=result.state.to_dict(),
            event=(
                result.event.to_dict()
                if result.event is not None
                else None
            ),
            metadata=deepcopy(
                metadata or {}
            ),
        )

    @staticmethod
    def timeline_command_response(
        result: ReviewTimelineCommandResult,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> ReviewTimelineCommandResponse:
        response_metadata = deepcopy(
            result.metadata
        )

        response_metadata.update(
            {
                "previous_revision": (
                    result.previous_revision
                ),
                "current_revision": (
                    result.current_revision
                ),
                "expected_revision": (
                    result.expected_revision
                ),
            }
        )

        response_metadata.update(
            deepcopy(metadata or {})
        )

        return ReviewTimelineCommandResponse(
            operation=(
                ReviewTimelineCommandOperation(
                    result.operation.value
                )
            ),
            production_id=(
                result.production_id
            ),
            session_id=result.session_id,
            snapshot=(
                result.snapshot.to_dict()
            ),
            command=result.command,
            event=result.event,
            history=result.history,
            metadata=response_metadata,
        )

    @staticmethod
    def clipboard_command_response(
        result: ReviewClipboardCommandResult,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> ReviewClipboardCommandResponse:
        response_metadata = deepcopy(
            result.metadata
        )
        response_metadata.update(
            {
                "expected_revision": (
                    result.expected_revision
                ),
                "timeline_changed": (
                    result.timeline_changed
                ),
            }
        )
        response_metadata.update(
            deepcopy(metadata or {})
        )

        return ReviewClipboardCommandResponse(
            operation=ReviewClipboardOperation(
                result.operation.value
            ),
            production_id=result.production_id,
            session_id=result.session_id,
            previous_revision=(
                result.previous_revision
            ),
            current_revision=(
                result.current_revision
            ),
            snapshot=result.snapshot.to_dict(),
            clipboard=result.clipboard,
            timeline_history=(
                result.timeline_history
            ),
            metadata=response_metadata,
        )

    @staticmethod
    def error_response(
        error: Exception,
        *,
        production_id: str | None = None,
        session_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ReviewWorkspaceErrorResponse:
        code, message = (
            ReviewWorkspaceAPIMapper
            ._classify_error(error)
        )

        resolved_metadata = deepcopy(
            metadata or {}
        )

        if isinstance(
            error,
            ReviewWorkspaceApplicationError,
        ):
            production_id = (
                error.production_id
                or production_id
            )
            session_id = (
                error.session_id
                or session_id
            )

            application_payload = (
                error.to_dict()
            )

            for key in (
                "code",
                "message",
                "production_id",
                "session_id",
            ):
                application_payload.pop(
                    key,
                    None,
                )

            if application_payload:
                resolved_metadata[
                    "application_error"
                ] = application_payload

        return ReviewWorkspaceErrorResponse(
            error=ReviewWorkspaceAPIErrorDetail(
                code=code,
                message=message,
                technical_message=str(error),
                production_id=production_id,
                session_id=session_id,
                metadata=resolved_metadata,
            )
        )

    @staticmethod
    def _classify_error(
        error: Exception,
    ) -> tuple[
        ReviewWorkspaceAPIErrorCode,
        str,
    ]:
        if isinstance(
            error,
            ProductWorkspaceNotFoundError,
        ):
            return (
                ReviewWorkspaceAPIErrorCode
                .PRODUCTION_NOT_FOUND,
                "Không tìm thấy dự án video.",
            )

        if isinstance(
            error,
            ProductWorkspaceLoadError,
        ):
            return (
                ReviewWorkspaceAPIErrorCode
                .WORKSPACE_LOAD_FAILED,
                (
                    "Không thể tải không gian "
                    "chỉnh sửa video."
                ),
            )

        if isinstance(
            error,
            ReviewRuntimeSessionNotFoundError,
        ):
            return (
                ReviewWorkspaceAPIErrorCode
                .SESSION_NOT_FOUND,
                (
                    "Không tìm thấy phiên review "
                    "đang hoạt động."
                ),
            )

        if isinstance(
            error,
            ReviewRuntimeSessionConflictError,
        ):
            return (
                ReviewWorkspaceAPIErrorCode
                .SESSION_CONFLICT,
                (
                    "Phiên review đang xung đột "
                    "với yêu cầu hiện tại."
                ),
            )

        if isinstance(
            error,
            ReviewClipboardCommandOperationError,
        ):
            return (
                ReviewWorkspaceAPIErrorCode
                .CLIPBOARD_COMMAND_FAILED,
                (
                    "Không thể thực hiện thao tác "
                    "clipboard trên timeline."
                ),
            )

        if isinstance(
            error,
            ReviewRuntimeSessionOperationError,
        ):
            return (
                ReviewWorkspaceAPIErrorCode
                .SESSION_OPERATION_FAILED,
                (
                    "Không thể thực hiện thao tác "
                    "trên phiên review."
                ),
            )

        if isinstance(error, ValueError):
            return (
                ReviewWorkspaceAPIErrorCode
                .VALIDATION_ERROR,
                (
                    "Dữ liệu yêu cầu review "
                    "không hợp lệ."
                ),
            )

        return (
            ReviewWorkspaceAPIErrorCode
            .INTERNAL_ERROR,
            (
                "Đã xảy ra lỗi khi xử lý "
                "không gian review."
            ),
        )
