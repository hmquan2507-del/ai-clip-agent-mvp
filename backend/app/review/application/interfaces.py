from __future__ import annotations

from abc import ABC, abstractmethod

from app.review.session.models import (
    ReviewRuntimeSessionResult,
    ReviewRuntimeSessionSnapshot,
)
from app.review.session.runtime import ReviewRuntimeSession


class ReviewWorkspaceApplicationServiceInterface(ABC):
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
    def cleanup_expired_sessions(self) -> list[str]:
        raise NotImplementedError