from __future__ import annotations

from typing import Any, Protocol


class RenderQueueSubmissionPort(Protocol):
    def submit_render(
        self,
        *,
        production_id: str,
        payload: dict[str, Any],
        idempotency_key: str,
    ) -> str:
        ...

    def find_by_idempotency_key(self, idempotency_key: str) -> str | None:
        ...
