from __future__ import annotations

import time

from app.product.adapters import (
    ProductWorkspaceSnapshot,
)


class ProductWorkspaceCache:
    def __init__(
        self,
        ttl_seconds: float = 15.0,
    ):
        self.ttl_seconds = max(
            0.0,
            float(ttl_seconds),
        )

        self._values: dict[
            str,
            tuple[
                float,
                ProductWorkspaceSnapshot,
            ],
        ] = {}

    def get(
        self,
        production_id: str,
    ) -> ProductWorkspaceSnapshot | None:
        item = self._values.get(
            production_id
        )

        if item is None:
            return None

        stored_at, snapshot = item

        if (
            self.ttl_seconds > 0
            and time.monotonic() - stored_at
            > self.ttl_seconds
        ):
            self._values.pop(
                production_id,
                None,
            )
            return None

        return snapshot

    def set(
        self,
        production_id: str,
        snapshot: ProductWorkspaceSnapshot,
    ) -> None:
        self._values[
            production_id
        ] = (
            time.monotonic(),
            snapshot,
        )

    def invalidate(
        self,
        production_id: str,
    ) -> None:
        self._values.pop(
            production_id,
            None,
        )

    def clear(self) -> None:
        self._values.clear()