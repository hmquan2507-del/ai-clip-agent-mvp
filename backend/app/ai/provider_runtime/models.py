from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProviderRuntimeRequest:
    provider_key: str
    prompt_key: str
    variables: dict[str, Any] = field(default_factory=dict)
    model: str | None = None
    temperature: float = 0.2
    max_tokens: int | None = None
    required_keys: list[str] = field(default_factory=list)


@dataclass
class ProviderRuntimeResult:
    provider_key: str
    prompt_key: str
    text: str
    data: dict[str, Any] = field(default_factory=dict)
    is_valid: bool = True
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_key": self.provider_key,
            "prompt_key": self.prompt_key,
            "text": self.text,
            "data": self.data,
            "is_valid": self.is_valid,
            "errors": self.errors,
            "metadata": self.metadata,
        }