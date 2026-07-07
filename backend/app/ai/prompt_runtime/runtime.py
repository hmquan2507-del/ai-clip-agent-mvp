from __future__ import annotations

from typing import Any

from app.ai.prompt_runtime.loader import PromptLoader


class PromptRuntime:
    def __init__(self, loader: PromptLoader):
        self.loader = loader

    def render(
        self,
        prompt_key: str,
        variables: dict[str, Any],
    ) -> dict[str, str]:
        template = self.loader.get(prompt_key)
        return template.render(variables)