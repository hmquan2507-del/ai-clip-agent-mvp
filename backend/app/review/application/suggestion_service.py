from __future__ import annotations

from copy import deepcopy
from threading import RLock
from typing import Any

from app.review.application.suggestion_errors import (
    ReviewAISuggestionOperationError,
    ReviewAISuggestionRevisionConflictError,
)
from app.review.application.suggestion_interfaces import (
    AISuggestionRegeneratorInterface,
    ReviewAISuggestionApplicationServiceInterface,
)
from app.review.application.suggestion_models import (
    ReviewAISuggestionApplicationResult,
    ReviewAISuggestionOperation,
)
from app.review.suggestions.lifecycle_models import (
    AISuggestionLifecycleResult,
)
from app.review.suggestions.models import AISuggestionReadModel


class ReviewAISuggestionApplicationService(
    ReviewAISuggestionApplicationServiceInterface
):
    """Coordinate AI suggestions with the authoritative review session.

    The service never edits timeline objects. Applying a proposal delegates
    exactly one operation to ReviewWorkspaceApplicationService, which keeps
    history, revision validation and TimelineRuntimeStore ownership intact.
    """

    def __init__(
        self,
        *,
        workspace_service: Any,
        regenerator: AISuggestionRegeneratorInterface | Any | None = None,
    ):
        self.workspace_service = workspace_service
        self.regenerator = regenerator

        shared_lock = getattr(
            workspace_service,
            "operation_lock",
            None,
        )
        self._operation_lock = (
            shared_lock if shared_lock is not None else RLock()
        )

    @property
    def operation_lock(self):
        return self._operation_lock

    @property
    def uses_shared_operation_lock(self) -> bool:
        return (
            getattr(
                self.workspace_service,
                "operation_lock",
                None,
            )
            is self._operation_lock
        )

    def get_ai_suggestions(
        self,
        production_id: str,
        *,
        session_id: str,
    ) -> ReviewAISuggestionApplicationResult:
        with self._operation_lock:
            production_id, session_id, session = self._session(
                production_id,
                session_id,
            )
            return self._result(
                ReviewAISuggestionOperation.GET,
                production_id,
                session_id,
                session,
            )

    def select_ai_suggestion(
        self,
        production_id: str,
        *,
        session_id: str,
        suggestion_id: str | None,
        expected_lifecycle_revision: int | None = None,
    ) -> ReviewAISuggestionApplicationResult:
        with self._operation_lock:
            production_id, session_id, session = self._session(
                production_id,
                session_id,
            )
            suggestion_id = self._optional_id(
                suggestion_id,
                field_name="suggestion_id",
            )
            runtime = session.graph.suggestion_runtime
            self._assert_lifecycle_revision(
                runtime.revision,
                expected_lifecycle_revision,
                production_id,
                session_id,
            )
            lifecycle_result = runtime.select(
                suggestion_id,
                expected_revision=expected_lifecycle_revision,
            )
            self._require_success(
                lifecycle_result,
                ReviewAISuggestionOperation.SELECT,
                production_id,
                session_id,
                suggestion_id,
            )
            return self._result(
                ReviewAISuggestionOperation.SELECT,
                production_id,
                session_id,
                session,
                lifecycle_result=lifecycle_result,
                metadata={"suggestion_id": suggestion_id},
            )

    def dismiss_ai_suggestion(
        self,
        production_id: str,
        *,
        session_id: str,
        suggestion_id: str,
        expected_lifecycle_revision: int | None = None,
    ) -> ReviewAISuggestionApplicationResult:
        with self._operation_lock:
            production_id, session_id, session = self._session(
                production_id,
                session_id,
            )
            suggestion_id = self._required_id(
                suggestion_id,
                field_name="suggestion_id",
            )
            runtime = session.graph.suggestion_runtime
            before_timeline = session.graph.timeline_store.snapshot()
            self._assert_lifecycle_revision(
                runtime.revision,
                expected_lifecycle_revision,
                production_id,
                session_id,
            )
            lifecycle_result = runtime.dismiss(
                suggestion_id,
                expected_revision=expected_lifecycle_revision,
            )
            self._require_success(
                lifecycle_result,
                ReviewAISuggestionOperation.DISMISS,
                production_id,
                session_id,
                suggestion_id,
            )
            self._assert_timeline_read_only(
                before_timeline,
                session.graph.timeline_store.snapshot(),
                production_id,
                session_id,
                ReviewAISuggestionOperation.DISMISS,
            )
            return self._result(
                ReviewAISuggestionOperation.DISMISS,
                production_id,
                session_id,
                session,
                lifecycle_result=lifecycle_result,
                metadata={"suggestion_id": suggestion_id},
            )

    def regenerate_ai_suggestions(
        self,
        production_id: str,
        *,
        session_id: str,
        expected_lifecycle_revision: int | None = None,
    ) -> ReviewAISuggestionApplicationResult:
        with self._operation_lock:
            production_id, session_id, session = self._session(
                production_id,
                session_id,
            )
            runtime = session.graph.suggestion_runtime
            before_timeline = session.graph.timeline_store.snapshot()
            self._assert_lifecycle_revision(
                runtime.revision,
                expected_lifecycle_revision,
                production_id,
                session_id,
            )
            current = runtime.snapshot()
            generated = self._regenerate(
                production_id=production_id,
                session_id=session_id,
                timeline_revision=before_timeline.revision,
                current=current,
            )
            if generated.production_id != production_id:
                raise self._operation_error(
                    "Regenerated suggestions use the wrong production_id.",
                    ReviewAISuggestionOperation.REGENERATE,
                    production_id,
                    session_id,
                )
            if generated.timeline_revision != before_timeline.revision:
                raise self._operation_error(
                    "Regenerated suggestions use a stale timeline revision.",
                    ReviewAISuggestionOperation.REGENERATE,
                    production_id,
                    session_id,
                )

            lifecycle_result = runtime.regenerate(
                generated,
                expected_revision=expected_lifecycle_revision,
            )
            self._require_success(
                lifecycle_result,
                ReviewAISuggestionOperation.REGENERATE,
                production_id,
                session_id,
                None,
            )
            self._assert_timeline_read_only(
                before_timeline,
                session.graph.timeline_store.snapshot(),
                production_id,
                session_id,
                ReviewAISuggestionOperation.REGENERATE,
            )
            return self._result(
                ReviewAISuggestionOperation.REGENERATE,
                production_id,
                session_id,
                session,
                lifecycle_result=lifecycle_result,
            )

    def apply_ai_suggestion(
        self,
        production_id: str,
        *,
        session_id: str,
        suggestion_id: str,
        expected_timeline_revision: int | None = None,
        expected_lifecycle_revision: int | None = None,
    ) -> ReviewAISuggestionApplicationResult:
        with self._operation_lock:
            production_id, session_id, session = self._session(
                production_id,
                session_id,
            )
            suggestion_id = self._required_id(
                suggestion_id,
                field_name="suggestion_id",
            )
            runtime = session.graph.suggestion_runtime
            before_timeline = session.graph.timeline_store.snapshot()
            source_revision = before_timeline.revision

            self._assert_timeline_revision(
                source_revision,
                expected_timeline_revision,
                production_id,
                session_id,
            )
            self._assert_lifecycle_revision(
                runtime.revision,
                expected_lifecycle_revision,
                production_id,
                session_id,
            )
            lifecycle_revision = runtime.revision
            preparation = runtime.prepare_apply(
                suggestion_id,
                active_timeline_revision=source_revision,
                expected_revision=expected_lifecycle_revision,
            )
            if not preparation.success or preparation.command is None:
                raise self._operation_error(
                    preparation.error or "AI suggestion cannot be applied.",
                    ReviewAISuggestionOperation.APPLY,
                    production_id,
                    session_id,
                    suggestion_id,
                )

            timeline_result = self._execute_proposal(
                production_id,
                session_id,
                preparation.command.operation,
                preparation.command.arguments,
                source_revision,
            )
            resulting_revision = int(timeline_result.current_revision)
            lifecycle_result = runtime.mark_applied(
                suggestion_id,
                source_timeline_revision=source_revision,
                resulting_timeline_revision=resulting_revision,
                expected_revision=lifecycle_revision,
            )
            self._require_success(
                lifecycle_result,
                ReviewAISuggestionOperation.APPLY,
                production_id,
                session_id,
                suggestion_id,
            )
            return self._result(
                ReviewAISuggestionOperation.APPLY,
                production_id,
                session_id,
                session,
                lifecycle_result=lifecycle_result,
                timeline_command_result=timeline_result,
                metadata={
                    "suggestion_id": suggestion_id,
                    "command_operation": preparation.command.operation,
                    "source_timeline_revision": source_revision,
                    "resulting_timeline_revision": resulting_revision,
                },
            )

    def _execute_proposal(
        self,
        production_id: str,
        session_id: str,
        operation: str,
        arguments: dict[str, Any],
        expected_revision: int,
    ) -> Any:
        operation = str(operation).strip()
        arguments = deepcopy(arguments)
        method_names = {
            "move_clip": "move_clip",
            "trim_clip_start": "trim_clip_start",
            "trim_clip_end": "trim_clip_end",
            "split_clip": "split_clip",
            "duplicate_clip": "duplicate_clip",
            "delete_clip": "delete_clip",
            "close_gap": "close_gap",
        }
        method_name = method_names.get(operation)
        if method_name is None:
            raise self._operation_error(
                f"Unsupported AI suggestion command: {operation}.",
                ReviewAISuggestionOperation.APPLY,
                production_id,
                session_id,
                metadata={"command_operation": operation},
            )

        executor = getattr(self.workspace_service, method_name, None)
        if not callable(executor):
            raise self._operation_error(
                f"Timeline command is unavailable: {operation}.",
                ReviewAISuggestionOperation.APPLY,
                production_id,
                session_id,
                metadata={"command_operation": operation},
            )
        reserved = {
            "production_id",
            "session_id",
            "expected_revision",
        }
        if reserved.intersection(arguments):
            raise self._operation_error(
                "AI suggestion command contains reserved arguments.",
                ReviewAISuggestionOperation.APPLY,
                production_id,
                session_id,
                metadata={"command_operation": operation},
            )
        try:
            return executor(
                production_id,
                session_id=session_id,
                expected_revision=expected_revision,
                **arguments,
            )
        except (ReviewAISuggestionOperationError,):
            raise
        except Exception:
            # Preserve the original timeline/application error contract.
            raise

    def _regenerate(
        self,
        *,
        production_id: str,
        session_id: str,
        timeline_revision: int,
        current: Any,
    ) -> AISuggestionReadModel:
        if self.regenerator is None:
            raise self._operation_error(
                "AI suggestion regenerator is not configured.",
                ReviewAISuggestionOperation.REGENERATE,
                production_id,
                session_id,
            )
        regenerate = getattr(self.regenerator, "regenerate", None)
        if not callable(regenerate) and callable(self.regenerator):
            regenerate = self.regenerator
        if not callable(regenerate):
            raise self._operation_error(
                "AI suggestion regenerator is invalid.",
                ReviewAISuggestionOperation.REGENERATE,
                production_id,
                session_id,
            )
        try:
            result = regenerate(
                production_id=production_id,
                session_id=session_id,
                timeline_revision=timeline_revision,
                current=current.clone(),
            )
        except ReviewAISuggestionOperationError:
            raise
        except Exception as error:
            raise self._operation_error(
                str(error),
                ReviewAISuggestionOperation.REGENERATE,
                production_id,
                session_id,
                metadata={"exception_type": type(error).__name__},
            ) from error
        if not isinstance(result, AISuggestionReadModel):
            raise self._operation_error(
                "AI suggestion regenerator returned an invalid read model.",
                ReviewAISuggestionOperation.REGENERATE,
                production_id,
                session_id,
            )
        return result.clone()

    def _session(
        self,
        production_id: str,
        session_id: str,
    ) -> tuple[str, str, Any]:
        production_id = self._required_id(
            production_id,
            field_name="production_id",
        )
        session_id = self._required_id(
            session_id,
            field_name="session_id",
        )
        session = self.workspace_service.get_session(
            production_id,
            session_id=session_id,
        )
        if getattr(session, "closed", False):
            raise self._operation_error(
                "Closed review runtime session cannot use AI suggestions.",
                ReviewAISuggestionOperation.GET,
                production_id,
                session_id,
            )
        return production_id, session_id, session

    def _result(
        self,
        operation: ReviewAISuggestionOperation,
        production_id: str,
        session_id: str,
        session: Any,
        *,
        lifecycle_result: AISuggestionLifecycleResult | None = None,
        timeline_command_result: Any | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ReviewAISuggestionApplicationResult:
        suggestion_snapshot = (
            lifecycle_result.snapshot
            if lifecycle_result is not None
            else session.graph.suggestion_runtime.snapshot()
        )
        return ReviewAISuggestionApplicationResult(
            operation=operation,
            production_id=production_id,
            session_id=session_id,
            workspace_snapshot=session.snapshot(),
            suggestion_snapshot=suggestion_snapshot,
            timeline_command_result=timeline_command_result,
            metadata=deepcopy(metadata or {}),
        )

    @staticmethod
    def _assert_timeline_revision(
        current: int,
        expected: int | None,
        production_id: str,
        session_id: str,
    ) -> None:
        if expected is not None and int(expected) != int(current):
            raise ReviewAISuggestionRevisionConflictError(
                "Timeline revision does not match expected revision.",
                production_id=production_id,
                session_id=session_id,
                expected_revision=int(expected),
                current_revision=int(current),
            )

    @staticmethod
    def _assert_lifecycle_revision(
        current: int,
        expected: int | None,
        production_id: str,
        session_id: str,
    ) -> None:
        if expected is not None and int(expected) != int(current):
            raise ReviewAISuggestionRevisionConflictError(
                "AI suggestion lifecycle revision does not match expected revision.",
                production_id=production_id,
                session_id=session_id,
                expected_revision=int(expected),
                current_revision=int(current),
            )

    @staticmethod
    def _assert_timeline_read_only(
        before: Any,
        after: Any,
        production_id: str,
        session_id: str,
        operation: ReviewAISuggestionOperation,
    ) -> None:
        before_payload = before.to_dict()
        after_payload = after.to_dict()
        if before_payload != after_payload:
            raise ReviewAISuggestionOperationError(
                "Read-only AI suggestion operation changed the timeline.",
                production_id=production_id,
                session_id=session_id,
                operation=operation.value,
            )

    @staticmethod
    def _require_success(
        result: AISuggestionLifecycleResult,
        operation: ReviewAISuggestionOperation,
        production_id: str,
        session_id: str,
        suggestion_id: str | None,
    ) -> None:
        if not result.success:
            raise ReviewAISuggestionOperationError(
                result.error or "AI suggestion operation failed.",
                production_id=production_id,
                session_id=session_id,
                operation=operation.value,
                suggestion_id=suggestion_id,
            )

    @staticmethod
    def _required_id(value: Any, *, field_name: str) -> str:
        normalized = str(value).strip()
        if not normalized:
            raise ValueError(f"{field_name} is required.")
        return normalized

    @staticmethod
    def _optional_id(
        value: Any | None,
        *,
        field_name: str,
    ) -> str | None:
        if value is None:
            return None
        normalized = str(value).strip()
        if not normalized:
            raise ValueError(f"{field_name} cannot be empty.")
        return normalized

    @staticmethod
    def _operation_error(
        message: str,
        operation: ReviewAISuggestionOperation,
        production_id: str,
        session_id: str,
        suggestion_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ReviewAISuggestionOperationError:
        return ReviewAISuggestionOperationError(
            message,
            production_id=production_id,
            session_id=session_id,
            operation=operation.value,
            suggestion_id=suggestion_id,
            metadata=metadata,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "service": "ReviewAISuggestionApplicationService",
            "contract_version": "16.6.3",
            "shared_operation_lock": self.uses_shared_operation_lock,
            "history_backed_apply": True,
            "direct_timeline_mutation": False,
            "operations": [
                operation.value
                for operation in ReviewAISuggestionOperation
            ],
            "regenerator_configured": self.regenerator is not None,
        }


def build_review_ai_suggestion_application_service(
    *,
    workspace_service: Any,
    regenerator: AISuggestionRegeneratorInterface | Any | None = None,
) -> ReviewAISuggestionApplicationService:
    return ReviewAISuggestionApplicationService(
        workspace_service=workspace_service,
        regenerator=regenerator,
    )
