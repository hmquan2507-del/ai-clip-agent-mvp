from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from threading import RLock
from typing import Any, Callable

from app.product.workspace.service import (
    ProductWorkspaceService,
)
from app.review.application.errors import (
    ReviewClipboardCommandOperationError,
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
    ReviewClipboardCommandResult,
    ReviewClipboardCommandType,
    ReviewTimelineCommandResult,
    ReviewTimelineCommandType,
)
from app.review.editing.clipboard.models import (
    TimelineClipboardResult,
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

ClipboardCommandExecutor = Callable[
    [ReviewRuntimeSession],
    TimelineClipboardResult,
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

    @property
    def operation_lock(self):
        """Return the shared application operation lock.

        Suggestion orchestration uses the same re-entrant lock as
        timeline and clipboard commands so proposal validation and
        history-backed execution observe one authoritative revision.
        """
        return self._timeline_command_lock

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
    def select_clip(
        self,
        production_id: str,
        *,
        session_id: str,
        clip_id: str,
        additive: bool = False,
        move_cursor: bool = False,
    ) -> ReviewRuntimeSessionSnapshot:
        normalized_id = self._normalize_id(
            production_id
        )
        normalized_session_id = str(
            session_id
        ).strip()
        normalized_clip_id = str(
            clip_id
        ).strip()

        if not normalized_session_id:
            raise ValueError(
                "session_id is required."
            )

        if not normalized_clip_id:
            raise ValueError(
                "clip_id is required."
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
                    ReviewRuntimeSessionOperationError(
                        (
                            "Closed review runtime "
                            "session cannot change "
                            "timeline selection."
                        ),
                        production_id=(
                            normalized_id
                        ),
                        session_id=(
                            normalized_session_id
                        ),
                    )
                )

            try:
                result = session.select_clip(
                    normalized_clip_id,
                    additive=bool(additive),
                    move_cursor=bool(
                        move_cursor
                    ),
                )
            except ReviewWorkspaceApplicationError:
                raise
            except Exception as error:
                raise (
                    ReviewRuntimeSessionOperationError(
                        str(error),
                        production_id=(
                            normalized_id
                        ),
                        session_id=(
                            normalized_session_id
                        ),
                    )
                ) from error

            if (
                not result.success
                or result.snapshot is None
            ):
                raise (
                    ReviewRuntimeSessionOperationError(
                        (
                            result.error
                            or (
                                "Timeline clip "
                                "selection failed."
                            )
                        ),
                        production_id=(
                            normalized_id
                        ),
                        session_id=(
                            normalized_session_id
                        ),
                    )
                )

            return result.snapshot.clone()

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

    def move_clips(
        self,
        production_id: str,
        *,
        session_id: str,
        clip_ids: list[str],
        delta_time: float,
        expected_revision: int | None = None,
    ) -> ReviewTimelineCommandResult:
        normalized_ids = self._normalize_clip_ids(clip_ids)
        if len(normalized_ids) < 2:
            raise ValueError("clip_ids must contain at least two unique clips.")
        return self._execute_timeline_command(
            production_id,
            session_id=session_id,
            operation=ReviewTimelineCommandType.MOVE_CLIPS,
            expected_revision=expected_revision,
            executor=lambda session: session.graph.history_runtime.move_clips(
                normalized_ids, float(delta_time)
            ),
            metadata={"clip_ids": normalized_ids, "delta_time": float(delta_time)},
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

    def duplicate_clips(
        self,
        production_id: str,
        *,
        session_id: str,
        clip_ids: list[str],
        time_offset: float | None = None,
        expected_revision: int | None = None,
    ) -> ReviewTimelineCommandResult:
        normalized_ids = self._normalize_clip_ids(clip_ids)
        if len(normalized_ids) < 2:
            raise ValueError("clip_ids must contain at least two unique clips.")
        return self._execute_timeline_command(
            production_id,
            session_id=session_id,
            operation=ReviewTimelineCommandType.DUPLICATE_CLIPS,
            expected_revision=expected_revision,
            executor=lambda session: session.graph.history_runtime.duplicate_clips(
                normalized_ids, time_offset=time_offset
            ),
            metadata={"clip_ids": normalized_ids, "time_offset": time_offset},
        )

    def delete_clips(
        self,
        production_id: str,
        *,
        session_id: str,
        clip_ids: list[str],
        expected_revision: int | None = None,
    ) -> ReviewTimelineCommandResult:
        normalized_ids = self._normalize_clip_ids(clip_ids)
        if len(normalized_ids) < 2:
            raise ValueError("clip_ids must contain at least two unique clips.")
        return self._execute_timeline_command(
            production_id,
            session_id=session_id,
            operation=ReviewTimelineCommandType.DELETE_CLIPS,
            expected_revision=expected_revision,
            executor=lambda session: session.graph.history_runtime.delete_clips(normalized_ids),
            metadata={"clip_ids": normalized_ids},
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

    def copy_timeline_clips(
        self,
        production_id: str,
        *,
        session_id: str,
        clip_ids: list[str],
        expected_revision: int | None = None,
    ) -> ReviewClipboardCommandResult:
        normalized_clip_ids = (
            self._normalize_clip_ids(clip_ids)
        )
        return self._execute_clipboard_command(
            production_id,
            session_id=session_id,
            operation=ReviewClipboardCommandType.COPY,
            expected_revision=expected_revision,
            executor=lambda session: (
                session.graph.clipboard_runtime
                .copy_clips(normalized_clip_ids)
            ),
            metadata={
                "clip_ids": normalized_clip_ids,
            },
        )

    def cut_timeline_clips(
        self,
        production_id: str,
        *,
        session_id: str,
        clip_ids: list[str],
        expected_revision: int | None = None,
    ) -> ReviewClipboardCommandResult:
        normalized_clip_ids = (
            self._normalize_clip_ids(clip_ids)
        )
        return self._execute_clipboard_command(
            production_id,
            session_id=session_id,
            operation=ReviewClipboardCommandType.CUT,
            expected_revision=expected_revision,
            executor=lambda session: (
                session.graph.clipboard_runtime
                .cut_clips(normalized_clip_ids)
            ),
            metadata={
                "clip_ids": normalized_clip_ids,
            },
        )

    def paste_timeline_clips(
        self,
        production_id: str,
        *,
        session_id: str,
        at_time: float,
        target_track_id: str | None = None,
        track_mapping: dict[str, str] | None = None,
        expected_revision: int | None = None,
    ) -> ReviewClipboardCommandResult:
        normalized_time = float(at_time)
        if normalized_time < 0.0:
            raise ValueError(
                "at_time must be greater than or "
                "equal to 0."
            )

        normalized_target_track_id = (
            self._normalize_optional_id(
                target_track_id,
                field_name="target_track_id",
            )
        )
        normalized_track_mapping = (
            self._normalize_track_mapping(
                track_mapping
            )
        )

        return self._execute_clipboard_command(
            production_id,
            session_id=session_id,
            operation=ReviewClipboardCommandType.PASTE,
            expected_revision=expected_revision,
            executor=lambda session: (
                session.graph.clipboard_runtime.paste(
                    at_time=normalized_time,
                    target_track_id=(
                        normalized_target_track_id
                    ),
                    track_mapping=(
                        normalized_track_mapping
                    ),
                )
            ),
            metadata={
                "at_time": normalized_time,
                "target_track_id": (
                    normalized_target_track_id
                ),
                "track_mapping": deepcopy(
                    normalized_track_mapping
                ),
            },
        )

    def restore_timeline_clipboard_history(
        self,
        production_id: str,
        *,
        session_id: str,
        entry_id: str,
        expected_revision: int | None = None,
    ) -> ReviewClipboardCommandResult:
        normalized_entry_id = str(entry_id).strip()
        if not normalized_entry_id:
            raise ValueError("entry_id is required.")

        return self._execute_clipboard_command(
            production_id,
            session_id=session_id,
            operation=(
                ReviewClipboardCommandType
                .RESTORE_HISTORY
            ),
            expected_revision=expected_revision,
            executor=lambda session: (
                session.graph.clipboard_runtime
                .restore_history_entry(
                    normalized_entry_id
                )
            ),
            metadata={
                "entry_id": normalized_entry_id,
            },
        )

    def clear_timeline_clipboard(
        self,
        production_id: str,
        *,
        session_id: str,
        expected_revision: int | None = None,
    ) -> ReviewClipboardCommandResult:
        return self._execute_clipboard_command(
            production_id,
            session_id=session_id,
            operation=(
                ReviewClipboardCommandType
                .CLEAR_CONTENT
            ),
            expected_revision=expected_revision,
            executor=lambda session: (
                session.graph.clipboard_runtime.clear()
            ),
        )

    def clear_timeline_clipboard_history(
        self,
        production_id: str,
        *,
        session_id: str,
        expected_revision: int | None = None,
    ) -> ReviewClipboardCommandResult:
        return self._execute_clipboard_command(
            production_id,
            session_id=session_id,
            operation=(
                ReviewClipboardCommandType
                .CLEAR_HISTORY
            ),
            expected_revision=expected_revision,
            executor=lambda session: (
                session.graph.clipboard_runtime
                .clear_history()
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
            "clipboard_commands": {
                "history_backed_mutations": True,
                "expected_revision": True,
                "shared_atomic_lock": True,
                "operations": [
                    operation.value
                    for operation
                    in ReviewClipboardCommandType
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

    def _execute_clipboard_command(
        self,
        production_id: str,
        *,
        session_id: str,
        operation: ReviewClipboardCommandType,
        executor: ClipboardCommandExecutor,
        expected_revision: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ReviewClipboardCommandResult:
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
                session_id=normalized_session_id,
            )
            if session.closed:
                raise ReviewClipboardCommandOperationError(
                    (
                        "Closed review runtime session "
                        "cannot execute clipboard "
                        "commands."
                    ),
                    production_id=normalized_id,
                    session_id=normalized_session_id,
                    operation=operation.value,
                )

            before_snapshot = session.snapshot()
            previous_revision = (
                before_snapshot.timeline.revision
            )
            if (
                normalized_expected_revision
                is not None
                and normalized_expected_revision
                != previous_revision
            ):
                raise ReviewTimelineRevisionConflictError(
                    (
                        "Timeline revision does not "
                        "match expected_revision."
                    ),
                    production_id=normalized_id,
                    session_id=normalized_session_id,
                    expected_revision=(
                        normalized_expected_revision
                    ),
                    current_revision=previous_revision,
                )

            try:
                clipboard_result = executor(session)
            except ReviewWorkspaceApplicationError:
                raise
            except Exception as error:
                raise ReviewClipboardCommandOperationError(
                    str(error),
                    production_id=normalized_id,
                    session_id=normalized_session_id,
                    operation=operation.value,
                    metadata={
                        "exception_type": (
                            type(error).__name__
                        ),
                    },
                ) from error

            if not clipboard_result.success:
                raise ReviewClipboardCommandOperationError(
                    (
                        clipboard_result.error
                        or "Clipboard command failed."
                    ),
                    production_id=normalized_id,
                    session_id=normalized_session_id,
                    operation=operation.value,
                    metadata={
                        "previous_revision": (
                            previous_revision
                        ),
                    },
                )

            after_snapshot = session.snapshot()
            clipboard_runtime = (
                session.graph.clipboard_runtime
            )
            return ReviewClipboardCommandResult(
                operation=operation,
                production_id=normalized_id,
                session_id=normalized_session_id,
                previous_revision=previous_revision,
                current_revision=(
                    after_snapshot.timeline.revision
                ),
                snapshot=after_snapshot,
                clipboard_result=clipboard_result,
                clipboard_history_state=(
                    clipboard_runtime.history_state()
                ),
                clipboard_history_entries=tuple(
                    clipboard_runtime.history_entries
                ),
                expected_revision=(
                    normalized_expected_revision
                ),
                metadata=deepcopy(metadata or {}),
            )

    @staticmethod
    def _normalize_clip_ids(
        clip_ids: list[str],
    ) -> list[str]:
        normalized = list(
            dict.fromkeys(
                str(clip_id).strip()
                for clip_id in clip_ids
                if str(clip_id).strip()
            )
        )
        if not normalized:
            raise ValueError(
                "clip_ids must contain at least "
                "one clip_id."
            )
        return normalized

    @staticmethod
    def _normalize_optional_id(
        value: str | None,
        *,
        field_name: str,
    ) -> str | None:
        if value is None:
            return None
        normalized = str(value).strip()
        if not normalized:
            raise ValueError(
                f"{field_name} cannot be empty."
            )
        return normalized

    @staticmethod
    def _normalize_track_mapping(
        mapping: dict[str, str] | None,
    ) -> dict[str, str] | None:
        if mapping is None:
            return None
        normalized: dict[str, str] = {}
        for source, target in mapping.items():
            source_id = str(source).strip()
            target_id = str(target).strip()
            if not source_id or not target_id:
                raise ValueError(
                    "track_mapping keys and values "
                    "cannot be empty."
                )
            normalized[source_id] = target_id
        return normalized
