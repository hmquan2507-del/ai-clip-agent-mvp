from __future__ import annotations

from pathlib import Path
from typing import Any

from app.product.workspace.interfaces import (
    QualityWorkspaceLoader,
)
from app.product.workspace.repository.utils import (
    call_first_supported,
    find_first_json,
    normalize_production_id,
)


class RepositoryQualityWorkspaceAdapter(
    QualityWorkspaceLoader
):
    METHOD_NAMES = (
        "get_latest_by_production_id",
        "find_latest_by_production_id",
        "get_by_production_id",
        "get_quality_report",
        "find_quality_report",
    )

    def __init__(
        self,
        quality_repository: Any | None = None,
        *,
        storage_roots: list[str | Path]
        | None = None,
    ):
        self.quality_repository = (
            quality_repository
        )

        self.storage_roots = [
            Path(item)
            for item in (
                storage_roots
                or [
                    "storage/production_render",
                    "storage/render_end_to_end_demo",
                    "storage/render_quality_test",
                ]
            )
        ]

    def load_quality_report(
        self,
        production_id: str,
    ) -> Any | None:
        normalized_id = (
            normalize_production_id(
                production_id
            )
        )

        repository_report = (
            call_first_supported(
                self.quality_repository,
                self.METHOD_NAMES,
                production_id=normalized_id,
                default=None,
            )
        )

        if repository_report is not None:
            return repository_report

        candidates: list[Path] = []

        for root in self.storage_roots:
            candidates.append(
                root
                / normalized_id
                / "artifacts"
                / "render_quality_report.json"
            )

        return find_first_json(
            candidates
        )