from __future__ import annotations

from app.providers.editing import get_editing_provider


class EditingEngine:
    async def generate(
        self,
        production_id: str,
        transcript: str,
        provider: str | None = "mock",
        target_duration_seconds: int | None = None,
    ) -> dict:
        editing_provider = get_editing_provider(provider)

        return await editing_provider.generate_editing_plan(
            production_id=production_id,
            transcript=transcript,
            target_duration_seconds=target_duration_seconds,
        )