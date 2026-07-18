from __future__ import annotations

from abc import ABC, abstractmethod

from app.review.application.models import (
    ReviewClipboardCommandResult,
    ReviewTimelineCommandResult,
)
from app.review.session.models import (
    ReviewRuntimeSessionResult,
    ReviewRuntimeSessionSnapshot,
)
from app.review.session.runtime import (
    ReviewRuntimeSession,
)


class ReviewWorkspaceApplicationServiceInterface(
    ABC
):
    @abstractmethod
    def open_session(
        self,
        production_id: str,
        *,
        force_refresh: bool = False,
        replace_existing: bool = False,
    ) -> ReviewRuntimeSession:
        raise NotImplementedError

    @abstractmethod
    def get_session(
        self,
        production_id: str,
        *,
        session_id: str | None = None,
    ) -> ReviewRuntimeSession:
        raise NotImplementedError

    @abstractmethod
    def get_snapshot(
        self,
        production_id: str,
        *,
        session_id: str | None = None,
    ) -> ReviewRuntimeSessionSnapshot:
        raise NotImplementedError

    @abstractmethod
    def reset_session(
        self,
        production_id: str,
        *,
        session_id: str,
    ) -> ReviewRuntimeSessionSnapshot:
        raise NotImplementedError

    @abstractmethod
    def close_session(
        self,
        production_id: str,
        *,
        session_id: str,
    ) -> ReviewRuntimeSessionResult:
        raise NotImplementedError

    @abstractmethod
    def select_clip(
        self,
        production_id: str,
        *,
        session_id: str,
        clip_id: str,
        additive: bool = False,
        move_cursor: bool = False,
    ) -> ReviewRuntimeSessionSnapshot:
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
    def trim_clip_start(
        self,
        production_id: str,
        *,
        session_id: str,
        clip_id: str,
        new_start_time: float,
        expected_revision: int | None = None,
    ) -> ReviewTimelineCommandResult:
        raise NotImplementedError

    @abstractmethod
    def trim_clip_end(
        self,
        production_id: str,
        *,
        session_id: str,
        clip_id: str,
        new_end_time: float,
        expected_revision: int | None = None,
    ) -> ReviewTimelineCommandResult:
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
    def delete_clip(
        self,
        production_id: str,
        *,
        session_id: str,
        clip_id: str,
        close_gap: bool = False,
        expected_revision: int | None = None,
    ) -> ReviewTimelineCommandResult:
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
    def undo_timeline(
        self,
        production_id: str,
        *,
        session_id: str,
        expected_revision: int | None = None,
    ) -> ReviewTimelineCommandResult:
        raise NotImplementedError

    @abstractmethod
    def redo_timeline(
        self,
        production_id: str,
        *,
        session_id: str,
        expected_revision: int | None = None,
    ) -> ReviewTimelineCommandResult:
        raise NotImplementedError

    @abstractmethod
    def cleanup_expired_sessions(
        self,
    ) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def copy_timeline_clips(
        self,
        production_id: str,
        *,
        session_id: str,
        clip_ids: list[str],
        expected_revision: int | None = None,
    ) -> ReviewClipboardCommandResult:
        raise NotImplementedError

    @abstractmethod
    def cut_timeline_clips(
        self,
        production_id: str,
        *,
        session_id: str,
        clip_ids: list[str],
        expected_revision: int | None = None,
    ) -> ReviewClipboardCommandResult:
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
    def restore_timeline_clipboard_history(
        self,
        production_id: str,
        *,
        session_id: str,
        entry_id: str,
        expected_revision: int | None = None,
    ) -> ReviewClipboardCommandResult:
        raise NotImplementedError

    @abstractmethod
    def clear_timeline_clipboard(
        self,
        production_id: str,
        *,
        session_id: str,
        expected_revision: int | None = None,
    ) -> ReviewClipboardCommandResult:
        raise NotImplementedError

    @abstractmethod
    def clear_timeline_clipboard_history(
        self,
        production_id: str,
        *,
        session_id: str,
        expected_revision: int | None = None,
    ) -> ReviewClipboardCommandResult:
        raise NotImplementedError
