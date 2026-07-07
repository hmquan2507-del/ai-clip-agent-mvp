from __future__ import annotations

from app.ai.prompt_runtime.models import PromptTemplate


class PromptLoader:
    def __init__(self):
        self._templates: dict[str, PromptTemplate] = {}

    def register(self, template: PromptTemplate) -> None:
        if not template.key:
            raise ValueError("Prompt key is required")

        self._templates[template.key] = template

    def get(self, key: str) -> PromptTemplate:
        template = self._templates.get(key)

        if template is None:
            raise ValueError(f"Prompt template not registered: {key}")

        return template

    def keys(self) -> list[str]:
        return sorted(self._templates.keys())