from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends

from app.review.export_api.service import ExportWorkspaceApplicationService


def create_export_service_dependency(
    provider: Callable[[], ExportWorkspaceApplicationService],
):
    """Create an explicit FastAPI dependency without hidden global state."""

    def dependency() -> ExportWorkspaceApplicationService:
        return provider()

    return Depends(dependency)
