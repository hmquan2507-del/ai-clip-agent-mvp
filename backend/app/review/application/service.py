from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.product.workspace.service import ProductWorkspaceService
from app.review.application.errors import (
    ReviewRuntimeSessionConflictError,
    ReviewRuntimeSessionNotFoundError,
    ReviewRuntimeSessionOperationError,
)
from app.review.application.interfaces import (
    ReviewWorkspaceApplicationServiceInterface,
)
from app.review.session.factory import build_review_runtime_session
from app.review.session.models import (
    ReviewRuntimeSessionResult,
    ReviewRuntimeSessionSnapshot,
)
from app.review.session.registry import (
    ReviewRuntimeSessionRegistryInterface,
)
from app.review.session.runtime import ReviewRuntimeSession


@dataclass(frozen=True)
class ReviewWorkspaceApplicationConfig:
    maximum_history_size: int = 100
    maximum_clipboard_history_size: int = 20

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "maximum_history_size",
            max(1, int(self.maximum_history_size)),
        )
        object.__setattr__(
            self,
            "maximum_clipboard_history_size",
            max(
                1,
                int(self.maximum_clipboard_history_size),
            ),
        )

    def to_dict(self) -> dict[str, int]:
        return {
            "maximum_history_size": self.maximum_history_size,
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
        product_workspace_service: ProductWorkspaceService,
        session_registry: ReviewRuntimeSessionRegistryInterface,
        config: ReviewWorkspaceApplicationConfig | None = None,
    ):
        self.product_workspace_service = product_workspace_service
        self.session_registry = session_registry
        self.config = (
            config or ReviewWorkspaceApplicationConfig()
        )

    def open_session(
        self,
        production_id: str,
        *,
        force_refresh: bool = False,
        replace_existing: bool = False,
    ) -> ReviewRuntimeSession:
        normalized_id = self._normalize_id(production_id)

        existing = self.session_registry.get(normalized_id)

        if existing is not None and not replace_existing:
            if force_refresh:
                raise ReviewRuntimeSessionConflictError(
                    (
                        "force_refresh requires replace_existing "
                        "when an active session exists."
                    ),
                    production_id=normalized_id,
                    session_id=existing.session_id,
                )

            return existing

        workspace = self.product_workspace_service.load_workspace(
            normalized_id,
            force_refresh=force_refresh,
            include_timeline_tracks=True,
        )

        workspace_production_id = str(
            workspace.production.production_id
        ).strip()

        if workspace_production_id != normalized_id:
            raise ReviewRuntimeSessionOperationError(
                (
                    "Loaded product workspace does not match "
                    "requested production_id."
                ),
                production_id=normalized_id,
            )

        candidate = build_review_runtime_session(
            workspace,
            maximum_history_size=(
                self.config.maximum_history_size
            ),
            maximum_clipboard_history_size=(
                self.config.maximum_clipboard_history_size
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

            if not replace_existing and not force_refresh:
                concurrent_session = self.session_registry.get(
                    normalized_id
                )

                if concurrent_session is not None:
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
        normalized_id = self._normalize_id(production_id)

        session = self.session_registry.get(
            normalized_id,
            session_id=session_id,
        )

        if session is None:
            raise ReviewRuntimeSessionNotFoundError(
                "Active review runtime session was not found.",
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

        if not result.success or result.snapshot is None:
            raise ReviewRuntimeSessionOperationError(
                result.error or "Review session reset failed.",
                production_id=session.production_id,
                session_id=session.session_id,
            )

        return result.snapshot.clone()

    def close_session(
        self,
        production_id: str,
        *,
        session_id: str,
    ) -> ReviewRuntimeSessionResult:
        normalized_id = self._normalize_id(production_id)

        session = self.session_registry.remove(
            normalized_id,
            session_id=session_id,
            close_session=False,
        )

        if session is None:
            raise ReviewRuntimeSessionNotFoundError(
                (
                    "Review runtime session could not be closed "
                    "because it was not found."
                ),
                production_id=normalized_id,
                session_id=session_id,
            )

        return session.close()

    def cleanup_expired_sessions(self) -> list[str]:
        return list(
            self.session_registry.cleanup_expired()
        )

    def to_dict(self) -> dict[str, Any]:
        registry_to_dict = getattr(
            self.session_registry,
            "to_dict",
            None,
        )

        return {
            "service": "ReviewWorkspaceApplicationService",
            "config": self.config.to_dict(),
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

    def _normalize_id(
        self,
        production_id: str,
    ) -> str:
        normalized = str(production_id).strip()

        if not normalized:
            raise ValueError(
                "production_id is required."
            )

        return normalized