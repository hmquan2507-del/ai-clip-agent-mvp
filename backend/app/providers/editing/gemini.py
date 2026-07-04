from __future__ import annotations

from app.providers.editing.base import BaseEditingProvider


class GeminiEditingProvider(BaseEditingProvider):
    async def generate_editing_plan(
        self,
        production_id: str,
        transcript: str,
        target_duration_seconds: int | None = None,
    ) -> dict:
        raise NotImplementedError(
            "Gemini editing provider is not implemented yet."
        )