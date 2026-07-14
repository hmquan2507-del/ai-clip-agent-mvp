from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from threading import RLock
from typing import Any, Callable

from app.product.workspace.service import (
    ProductWorkspaceService,
)
from app.review.application.errors import (
    ReviewRuntimeSessionConflictError,
    ReviewRuntimeSessionNotFoundError,
    ReviewRuntimeSessionOperationError,
    ReviewTimelineCommandOperationError,
    ReviewTimelineRevisionConflictError,
    ReviewWorkspaceApplicationError,
)
from app.review.application.interfaces import (
    ReviewWorkspaceApplicationServiceInterface,
)
from app.review.application.models import (
    ReviewTimelineCommandResult,
    ReviewTimelineCommandType,
)
from app.review.editing.history.models import (
    TimelineHistoryResult,
)
from app.review.session.factory import (
    build_review_runtime_session,
)
from app.review.session.models import (
    ReviewRuntimeSessionResult,
    ReviewRuntimeSessionSnapshot,
)
from app.review.session.registry import (
    ReviewRuntimeSessionRegistryInterface,
)
from app.review.session.runtime import (
    ReviewRuntimeSession,
)


TimelineCommandExecutor = Callable[
    [ReviewRuntimeSession],
    TimelineHistoryResult,
]


@dataclass(frozen=True)
class ReviewWorkspaceApplicationConfig:
    maximum_history_size: int = 100
    maximum_clipboard_history_size: int = 20

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "maximum_history_size",
            max(
                1,
                int(self.maximum_history_size),
            ),
        )
        object.__setattr__(
            self,
            "maximum_clipboard_history_size",
            max(
                1,
                int(
                    self.maximum_clipboard_history_size
                ),
            ),
        )

    def to_dict(self) -> dict[str, int]:
        return {
            "maximum_history_size": (
                self.maximum_history_size
            ),
            "maximum_clipboard_history_size": (
                self.maximum_clipboard_history_size
            ),
        }


class ReviewWorkspaceApplicationService(
    ReviewWorkspaceApplicationServiceInterface
):
    def __init__(
        self,
        *,
        product_workspace_service: (
            ProductWorkspaceService
        ),
        session_registry: (
            ReviewRuntimeSessionRegistryInterface
        ),
        config: (
            ReviewWorkspaceApplicationConfig
            | None
        ) = None,
    ):
        self.product_workspace_service = (
            product_workspace_service
        )
        self.session_registry = session_registry
        self.config = (
            config
            or ReviewWorkspaceApplicationConfig()
        )

        self._timeline_command_lock = RLock()

    def open_session(
        self,
        production_id: str,
        *,
        force_refresh: bool = False,
        replace_existing: bool = False,
    ) -> ReviewRuntimeSession:
        normalized_id = self._normalize_id(
            production_id
        )

        existing = self.session_registry.get(
            normalized_id
        )

        if (
            existing is not None
            and not replace_existing
        ):
            if force_refresh:
                raise (
                    ReviewRuntimeSessionConflictError(
                        (
                            "force_refresh requires "
                            "replace_existing when an "
                            "active session exists."
                        ),
                        production_id=normalized_id,
                        session_id=(
                            existing.session_id
                        ),
                    )
                )

            return existing

        workspace = (
            self.product_workspace_service
            .load_workspace(
                normalized_id,
                force_refresh=force_refresh,
                include_timeline_tracks=True,
            )
        )

        workspace_production_id = str(
            workspace.production.production_id
        ).strip()

        if (
            workspace_production_id
            != normalized_id
        ):
            raise ReviewRuntimeSessionOperationError(
                (
                    "Loaded product workspace does "
                    "not match requested "
                    "production_id."
                ),
                production_id=normalized_id,
            )

        candidate = build_review_runtime_session(
            workspace,
            maximum_history_size=(
                self.config.maximum_history_size
            ),
            maximum_clipboard_history_size=(
                self.config
                .maximum_clipboard_history_size
            ),
        )

        try:
            return self.session_registry.register(
                candidate,
                replace_existing=replace_existing,
                metadata={
                    "application_service": (
                        "ReviewWorkspaceApplicationService"
                    ),
                },
            )
        except ValueError as error:
            if not candidate.closed:
                candidate.close()

            if (
                not replace_existing
                and not force_refresh
            ):
                concurrent_session = (
                    self.session_registry.get(
                        normalized_id
                    )
                )

                if (
                    concurrent_session
                    is not None
                ):
                    return concurrent_session

            raise ReviewRuntimeSessionConflictError(
                str(error),
                production_id=normalized_id,
            ) from error

    def get_session(
        self,
        production_id: str,
        *,
        session_id: str | None = None,
    ) -> ReviewRuntimeSession:
        normalized_id = self._normalize_id(
            production_id
        )

        session = self.session_registry.get(
            normalized_id,
            session_id=session_id,
        )

        if session is None:
            raise ReviewRuntimeSessionNotFoundError(
                (
                    "Active review runtime session "
                    "was not found."
                ),
                production_id=normalized_id,
                session_id=session_id,
            )

        return session

    def get_snapshot(
        self,
        production_id: str,
        *,
        session_id: str | None = None,
    ) -> ReviewRuntimeSessionSnapshot:
        return self.get_session(
            production_id,
            session_id=session_id,
        ).snapshot()

    def reset_session(
        self,
        production_id: str,
        *,
        session_id: str,
    ) -> ReviewRuntimeSessionSnapshot:
        session = self.get_session(
            production_id,
            session_id=session_id,
        )

        result = session.reset()

        if (
            not result.success
            or result.snapshot is None
        ):
            raise (
                ReviewRuntimeSessionOperationError(
                    (
                        result.error
                        or (
                            "Review session reset "
                            "failed."
                        )
                    ),
                    production_id=(
                        session.production_id
                    ),
                    session_id=(
                        session.session_id
                    ),
                )
            )

        return result.snapshot.clone()

    def close_session(
        self,
        production_id: str,
        *,
        session_id: str,
    ) -> ReviewRuntimeSessionResult:
        normalized_id = self._normalize_id(
            production_id
        )

        session = self.session_registry.remove(
            normalized_id,
            session_id=session_id,
            close_session=False,
        )

        if session is None:
            raise ReviewRuntimeSessionNotFoundError(
                (
                    "Review runtime session could "
                    "not be closed because it was "
                    "not found."
                ),
                production_id=normalized_id,
                session_id=session_id,
            )

        return session.close()

    def move_clip(
        self,
        production_id: str,
        *,
        session_id: str,
        clip_id: str,
        new_start_time: float,
        target_track_id: str | None = None,
        expected_revision: int | None = None,
    ) -> ReviewTimelineCommandResult:
        return self._execute_timeline_command(
            production_id,
            session_id=session_id,
            operation=(
                ReviewTimelineCommandType.MOVE_CLIP
            ),
            expected_revision=expected_revision,
            executor=lambda session: (
                session.graph.history_runtime
                .move_clip(
                    clip_id,
                    new_start_time,
                    target_track_id=(
                        target_track_id
                    ),
                )
            ),
            metadata={
                "clip_id": clip_id,
                "new_start_time": (
                    float(new_start_time)
                ),
                "target_track_id": (
                    target_track_id
                ),
            },
        )

    def trim_clip_start(
        self,
        production_id: str,
        *,
        session_id: str,
        clip_id: str,
        new_start_time: float,
        expected_revision: int | None = None,
    ) -> ReviewTimelineCommandResult:
        return self._execute_timeline_command(
            production_id,
            session_id=session_id,
            operation=(
                ReviewTimelineCommandType
                .TRIM_CLIP_START
            ),
            expected_revision=expected_revision,
            executor=lambda session: (
                session.graph.history_runtime
                .trim_clip_start(
                    clip_id,
                    new_start_time,
                )
            ),
            metadata={
                "clip_id": clip_id,
                "new_start_time": (
                    float(new_start_time)
                ),
            },
        )

    def trim_clip_end(
        self,
        production_id: str,
        *,
        session_id: str,
        clip_id: str,
        new_end_time: float,
        expected_revision: int | None = None,
    ) -> ReviewTimelineCommandResult:
        return self._execute_timeline_command(
            production_id,
            session_id=session_id,
            operation=(
                ReviewTimelineCommandType
                .TRIM_CLIP_END
            ),
            expected_revision=expected_revision,
            executor=lambda session: (
                session.graph.history_runtime
                .trim_clip_end(
                    clip_id,
                    new_end_time,
                )
            ),
            metadata={
                "clip_id": clip_id,
                "new_end_time": (
                    float(new_end_time)
                ),
            },
        )

    def split_clip(
        self,
        production_id: str,
        *,
        session_id: str,
        clip_id: str,
        split_time: float,
        right_clip_id: str | None = None,
        expected_revision: int | None = None,
    ) -> ReviewTimelineCommandResult:
        return self._execute_timeline_command(
            production_id,
            session_id=session_id,
            operation=(
                ReviewTimelineCommandType
                .SPLIT_CLIP
            ),
            expected_revision=expected_revision,
            executor=lambda session: (
                session.graph.history_runtime
                .split_clip(
                    clip_id,
                    split_time,
                    right_clip_id=(
                        right_clip_id
                    ),
                )
            ),
            metadata={
                "clip_id": clip_id,
                "split_time": (
                    float(split_time)
                ),
                "right_clip_id": (
                    right_clip_id
                ),
            },
        )

    def duplicate_clip(
        self,
        production_id: str,
        *,
        session_id: str,
        clip_id: str,
        new_clip_id: str | None = None,
        new_start_time: float | None = None,
        target_track_id: str | None = None,
        expected_revision: int | None = None,
    ) -> ReviewTimelineCommandResult:
        return self._execute_timeline_command(
            production_id,
            session_id=session_id,
            operation=(
                ReviewTimelineCommandType
                .DUPLICATE_CLIP
            ),
            expected_revision=expected_revision,
            executor=lambda session: (
                session.graph.history_runtime
                .duplicate_clip(
                    clip_id,
                    new_clip_id=new_clip_id,
                    new_start_time=new_start_time,
                    target_track_id=(
                        target_track_id
                    ),
                )
            ),
            metadata={
                "clip_id": clip_id,
                "new_clip_id": new_clip_id,
                "new_start_time": (
                    new_start_time
                ),
                "target_track_id": (
                    target_track_id
                ),
            },
        )

    def delete_clip(
        self,
        production_id: str,
        *,
        session_id: str,
        clip_id: str,
        close_gap: bool = False,
        expected_revision: int | None = None,
    ) -> ReviewTimelineCommandResult:
        return self._execute_timeline_command(
            production_id,
            session_id=session_id,
            operation=(
                ReviewTimelineCommandType
                .DELETE_CLIP
            ),
            expected_revision=expected_revision,
            executor=lambda session: (
                session.graph.history_runtime
                .delete_clip(
                    clip_id,
                    close_gap=close_gap,
                )
            ),
            metadata={
                "clip_id": clip_id,
                "close_gap": bool(close_gap),
            },
        )

    def close_gap(
        self,
        production_id: str,
        *,
        session_id: str,
        track_id: str,
        gap_start: float,
        gap_end: float,
        expected_revision: int | None = None,
    ) -> ReviewTimelineCommandResult:
        return self._execute_timeline_command(
            production_id,
            session_id=session_id,
            operation=(
                ReviewTimelineCommandType
                .CLOSE_GAP
            ),
            expected_revision=expected_revision,
            executor=lambda session: (
                session.graph.history_runtime
                .close_gap(
                    track_id,
                    gap_start,
                    gap_end,
                )
            ),
            metadata={
                "track_id": track_id,
                "gap_start": float(
                    gap_start
                ),
                "gap_end": float(
                    gap_end
                ),
            },
        )

    def undo_timeline(
        self,
        production_id: str,
        *,
        session_id: str,
        expected_revision: int | None = None,
    ) -> ReviewTimelineCommandResult:
        return self._execute_timeline_command(
            production_id,
            session_id=session_id,
            operation=(
                ReviewTimelineCommandType.UNDO
            ),
            expected_revision=expected_revision,
            executor=lambda session: (
                session.graph.history_runtime
                .undo()
            ),
        )

    def redo_timeline(
        self,
        production_id: str,
        *,
        session_id: str,
        expected_revision: int | None = None,
    ) -> ReviewTimelineCommandResult:
        return self._execute_timeline_command(
            production_id,
            session_id=session_id,
            operation=(
                ReviewTimelineCommandType.REDO
            ),
            expected_revision=expected_revision,
            executor=lambda session: (
                session.graph.history_runtime
                .redo()
            ),
        )

    def cleanup_expired_sessions(
        self,
    ) -> list[str]:
        return list(
            self.session_registry
            .cleanup_expired()
        )

    def to_dict(self) -> dict[str, Any]:
        registry_to_dict = getattr(
            self.session_registry,
            "to_dict",
            None,
        )

        return {
            "service": (
                "ReviewWorkspaceApplicationService"
            ),
            "config": self.config.to_dict(),
            "timeline_commands": {
                "history_backed": True,
                "expected_revision": True,
                "atomic_lock": True,
                "operations": [
                    operation.value
                    for operation
                    in ReviewTimelineCommandType
                ],
            },
            "registry": (
                registry_to_dict()
                if callable(registry_to_dict)
                else {
                    "type": type(
                        self.session_registry
                    ).__name__,
                }
            ),
        }

    def _execute_timeline_command(
        self,
        production_id: str,
        *,
        session_id: str,
        operation: ReviewTimelineCommandType,
        executor: TimelineCommandExecutor,
        expected_revision: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ReviewTimelineCommandResult:
        normalized_id = self._normalize_id(
            production_id
        )
        normalized_session_id = str(
            session_id
        ).strip()

        if not normalized_session_id:
            raise ValueError(
                "session_id is required."
            )

        normalized_expected_revision = (
            int(expected_revision)
            if expected_revision is not None
            else None
        )

        if (
            normalized_expected_revision
            is not None
            and normalized_expected_revision < 1
        ):
            raise ValueError(
                "expected_revision must be "
                "greater than or equal to 1."
            )

        with self._timeline_command_lock:
            session = self.get_session(
                normalized_id,
                session_id=(
                    normalized_session_id
                ),
            )

            if session.closed:
                raise (
                    ReviewTimelineCommandOperationError(
                        (
                            "Closed review runtime "
                            "session cannot execute "
                            "timeline commands."
                        ),
                        production_id=normalized_id,
                        session_id=(
                            normalized_session_id
                        ),
                        operation=operation.value,
                    )
                )

            before_snapshot = (
                session.snapshot()
            )
            previous_revision = (
                before_snapshot.timeline.revision
            )

            if (
                normalized_expected_revision
                is not None
                and normalized_expected_revision
                != previous_revision
            ):
                raise (
                    ReviewTimelineRevisionConflictError(
                        (
                            "Timeline revision does "
                            "not match "
                            "expected_revision."
                        ),
                        production_id=normalized_id,
                        session_id=(
                            normalized_session_id
                        ),
                        expected_revision=(
                            normalized_expected_revision
                        ),
                        current_revision=(
                            previous_revision
                        ),
                    )
                )

            try:
                history_result = executor(
                    session
                )
            except ReviewWorkspaceApplicationError:
                raise
            except Exception as error:
                raise (
                    ReviewTimelineCommandOperationError(
                        str(error),
                        production_id=normalized_id,
                        session_id=(
                            normalized_session_id
                        ),
                        operation=operation.value,
                        metadata={
                            "exception_type": (
                                type(error).__name__
                            ),
                        },
                    )
                ) from error

            if not history_result.success:
                raise (
                    ReviewTimelineCommandOperationError(
                        (
                            history_result.error
                            or (
                                "Timeline command "
                                "failed."
                            )
                        ),
                        production_id=normalized_id,
                        session_id=(
                            normalized_session_id
                        ),
                        operation=operation.value,
                        metadata={
                            "previous_revision": (
                                previous_revision
                            ),
                        },
                    )
                )

            after_snapshot = (
                session.snapshot()
            )

            return ReviewTimelineCommandResult(
                operation=operation,
                production_id=normalized_id,
                session_id=(
                    normalized_session_id
                ),
                previous_revision=(
                    previous_revision
                ),
                current_revision=(
                    after_snapshot
                    .timeline.revision
                ),
                expected_revision=(
                    normalized_expected_revision
                ),
                snapshot=after_snapshot,
                history_result=(
                    history_result
                ),
                metadata=deepcopy(
                    metadata or {}
                ),
            )

    def _normalize_id(
        self,
        production_id: str,
    ) -> str:
        normalized = str(
            production_id
        ).strip()

        if not normalized:
            raise ValueError(
                "production_id is required."
            )

        return normalized