from __future__ import annotations

from typing import Any

from app.product.workspace.interfaces import (
    ProductionWorkspaceLoader,
)
from app.product.workspace.repository.utils import (
    call_first_supported,
    normalize_production_id,
)


class RepositoryProductionWorkspaceAdapter(
    ProductionWorkspaceLoader
):
    METHOD_NAMES = (
        "get_by_id",
        "find_by_id",
        "get",
        "get_production",
        "find",
    )

    def __init__(
        self,
        production_repository: Any,
    ):
        self.production_repository = (
            production_repository
        )

    def load_production(
        self,
        production_id: str,
    ) -> Any | None:
        normalized_id = (
            normalize_production_id(
                production_id
            )
        )

        return call_first_supported(
            self.production_repository,
            self.METHOD_NAMES,
            production_id=normalized_id,
            required=True,
        )