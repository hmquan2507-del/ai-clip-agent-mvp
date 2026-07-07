from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PromptTemplate:
    key: str
    system_prompt: str
    user_prompt: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def render(self, variables: dict[str, Any]) -> dict[str, str]:
        return {
            "system_prompt": self.system_prompt.format(**variables),
            "prompt": self.user_prompt.format(**variables),
        }