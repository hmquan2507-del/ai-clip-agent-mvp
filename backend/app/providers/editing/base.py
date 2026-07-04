from __future__ import annotations

from abc import ABC, abstractmethod


class BaseEditingProvider(ABC):
    @abstractmethod
    async def generate_editing_plan(
        self,
        production_id: str,
        transcript: str,
        target_duration_seconds: int | None = None,
    ) -> dict:
        raise NotImplementedError