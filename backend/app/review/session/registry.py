from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta, timezone
from threading import RLock
from typing import Any

from app.review.session.runtime import (
    ReviewRuntimeSession,
)


RegistryClock = Callable[[], datetime]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class ReviewRuntimeSessionRegistryEntry:
    production_id: str
    session_id: str

    registered_at: datetime
    last_accessed_at: datetime
    expires_at: datetime

    access_count: int = 0

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def is_expired(
        self,
        now: datetime,
    ) -> bool:
        return now >= self.expires_at

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "session_id": self.session_id,
            "registered_at": (
                self.registered_at.isoformat()
            ),
            "last_accessed_at": (
                self.last_accessed_at.isoformat()
            ),
            "expires_at": (
                self.expires_at.isoformat()
            ),
            "access_count": self.access_count,
            "metadata": deepcopy(
                self.metadata
            ),
        }


class ReviewRuntimeSessionRegistryInterface(
    ABC
):
    @abstractmethod
    def register(
        self,
        session: ReviewRuntimeSession,
        *,
        replace_existing: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> ReviewRuntimeSession:
        raise NotImplementedError

    @abstractmethod
    def get(
        self,
        production_id: str,
        *,
        session_id: str | None = None,
        touch: bool = True,
    ) -> ReviewRuntimeSession | None:
        raise NotImplementedError

    @abstractmethod
    def remove(
        self,
        production_id: str,
        *,
        session_id: str | None = None,
        close_session: bool = True,
    ) -> ReviewRuntimeSession | None:
        raise NotImplementedError

    @abstractmethod
    def cleanup_expired(
        self,
    ) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def clear(
        self,
        *,
        close_sessions: bool = True,
    ) -> list[str]:
        raise NotImplementedError


@dataclass
class _StoredSession:
    session: ReviewRuntimeSession
    entry: ReviewRuntimeSessionRegistryEntry


class InMemoryReviewRuntimeSessionRegistry(
    ReviewRuntimeSessionRegistryInterface
):
    def __init__(
        self,
        *,
        ttl_seconds: float = 1800.0,
        clock: RegistryClock | None = None,
    ):
        self.ttl_seconds = max(
            1.0,
            float(ttl_seconds),
        )
        self._clock = clock or utc_now
        self._lock = RLock()
        self._sessions: dict[
            str,
            _StoredSession,
        ] = {}

    @property
    def count(self) -> int:
        with self._lock:
            return len(self._sessions)

    @property
    def production_ids(
        self,
    ) -> tuple[str, ...]:
        with self._lock:
            return tuple(
                self._sessions.keys()
            )

    @property
    def entries(
        self,
    ) -> list[
        ReviewRuntimeSessionRegistryEntry
    ]:
        with self._lock:
            return deepcopy(
                [
                    stored.entry
                    for stored
                    in self._sessions.values()
                ]
            )

    def register(
        self,
        session: ReviewRuntimeSession,
        *,
        replace_existing: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> ReviewRuntimeSession:
        if session.closed:
            raise ValueError(
                "Closed review runtime session "
                "cannot be registered."
            )

        production_id = self._normalize_id(
            session.production_id,
            field_name="production_id",
        )

        session_id = self._normalize_id(
            session.session_id,
            field_name="session_id",
        )

        replaced_session: (
            ReviewRuntimeSession | None
        ) = None

        with self._lock:
            existing = self._sessions.get(
                production_id
            )

            if existing is not None:
                if (
                    existing.session.session_id
                    == session_id
                ):
                    self._touch_locked(
                        production_id,
                    )
                    return existing.session

                if not replace_existing:
                    raise ValueError(
                        "An active review runtime "
                        "session is already registered "
                        "for this production."
                    )

                replaced_session = (
                    existing.session
                )

            now = self._now()

            entry = (
                ReviewRuntimeSessionRegistryEntry(
                    production_id=production_id,
                    session_id=session_id,
                    registered_at=now,
                    last_accessed_at=now,
                    expires_at=(
                        now
                        + timedelta(
                            seconds=(
                                self.ttl_seconds
                            )
                        )
                    ),
                    access_count=0,
                    metadata=deepcopy(
                        metadata or {}
                    ),
                )
            )

            self._sessions[production_id] = (
                _StoredSession(
                    session=session,
                    entry=entry,
                )
            )

        if (
            replaced_session is not None
            and not replaced_session.closed
        ):
            replaced_session.close()

        return session

    def get(
        self,
        production_id: str,
        *,
        session_id: str | None = None,
        touch: bool = True,
    ) -> ReviewRuntimeSession | None:
        normalized_production_id = (
            self._normalize_id(
                production_id,
                field_name="production_id",
            )
        )

        normalized_session_id = (
            self._normalize_optional_id(
                session_id
            )
        )

        expired_session: (
            ReviewRuntimeSession | None
        ) = None

        with self._lock:
            stored = self._sessions.get(
                normalized_production_id
            )

            if stored is None:
                return None

            if (
                normalized_session_id
                is not None
                and stored.session.session_id
                != normalized_session_id
            ):
                return None

            if (
                stored.session.closed
                or stored.entry.is_expired(
                    self._now()
                )
            ):
                expired_session = (
                    stored.session
                )
                del self._sessions[
                    normalized_production_id
                ]
            else:
                if touch:
                    self._touch_locked(
                        normalized_production_id
                    )

                return stored.session

        if (
            expired_session is not None
            and not expired_session.closed
        ):
            expired_session.close()

        return None

    def remove(
        self,
        production_id: str,
        *,
        session_id: str | None = None,
        close_session: bool = True,
    ) -> ReviewRuntimeSession | None:
        normalized_production_id = (
            self._normalize_id(
                production_id,
                field_name="production_id",
            )
        )

        normalized_session_id = (
            self._normalize_optional_id(
                session_id
            )
        )

        with self._lock:
            stored = self._sessions.get(
                normalized_production_id
            )

            if stored is None:
                return None

            if (
                normalized_session_id
                is not None
                and stored.session.session_id
                != normalized_session_id
            ):
                return None

            del self._sessions[
                normalized_production_id
            ]

        if (
            close_session
            and not stored.session.closed
        ):
            stored.session.close()

        return stored.session

    def cleanup_expired(
        self,
    ) -> list[str]:
        sessions_to_close: list[
            ReviewRuntimeSession
        ] = []

        with self._lock:
            now = self._now()

            expired_production_ids = [
                production_id
                for production_id, stored
                in self._sessions.items()
                if (
                    stored.session.closed
                    or stored.entry.is_expired(now)
                )
            ]

            removed_session_ids: list[str] = []

            for production_id in (
                expired_production_ids
            ):
                stored = self._sessions.pop(
                    production_id
                )
                removed_session_ids.append(
                    stored.session.session_id
                )
                sessions_to_close.append(
                    stored.session
                )

        for session in sessions_to_close:
            if not session.closed:
                session.close()

        return removed_session_ids

    def clear(
        self,
        *,
        close_sessions: bool = True,
    ) -> list[str]:
        with self._lock:
            stored_sessions = list(
                self._sessions.values()
            )
            self._sessions.clear()

        if close_sessions:
            for stored in stored_sessions:
                if not stored.session.closed:
                    stored.session.close()

        return [
            stored.session.session_id
            for stored in stored_sessions
        ]

    def contains(
        self,
        production_id: str,
        *,
        session_id: str | None = None,
    ) -> bool:
        return (
            self.get(
                production_id,
                session_id=session_id,
                touch=False,
            )
            is not None
        )

    def to_dict(self) -> dict[str, Any]:
        with self._lock:
            entries = [
                stored.entry.to_dict()
                for stored
                in self._sessions.values()
            ]

        return {
            "registry": (
                "InMemoryReviewRuntimeSessionRegistry"
            ),
            "ttl_seconds": self.ttl_seconds,
            "session_count": len(entries),
            "entries": entries,
        }

    def _touch_locked(
        self,
        production_id: str,
    ) -> None:
        stored = self._sessions[
            production_id
        ]
        now = self._now()

        stored.entry = replace(
            stored.entry,
            last_accessed_at=now,
            expires_at=(
                now
                + timedelta(
                    seconds=self.ttl_seconds
                )
            ),
            access_count=(
                stored.entry.access_count + 1
            ),
        )

    def _now(self) -> datetime:
        value = self._clock()

        if value.tzinfo is None:
            return value.replace(
                tzinfo=timezone.utc
            )

        return value.astimezone(
            timezone.utc
        )

    def _normalize_id(
        self,
        value: str,
        *,
        field_name: str,
    ) -> str:
        normalized = str(value).strip()

        if not normalized:
            raise ValueError(
                f"{field_name} is required."
            )

        return normalized

    def _normalize_optional_id(
        self,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = str(value).strip()
        return normalized or None


def build_in_memory_review_runtime_session_registry(
    *,
    ttl_seconds: float = 1800.0,
    clock: RegistryClock | None = None,
) -> InMemoryReviewRuntimeSessionRegistry:
    return InMemoryReviewRuntimeSessionRegistry(
        ttl_seconds=ttl_seconds,
        clock=clock,
    )