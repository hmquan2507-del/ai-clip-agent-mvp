from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AIProviderRequest:
    prompt: str
    system_prompt: str | None = None
    model: str | None = None
    temperature: float = 0.2
    max_tokens: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AIProviderJSONRequest(AIProviderRequest):
    schema: dict[str, Any] = field(default_factory=dict)


@dataclass
class AIProviderEmbeddingRequest:
    input_text: str
    model: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AIProviderVisionRequest:
    prompt: str
    image_paths: list[str] = field(default_factory=list)
    video_frame_paths: list[str] = field(default_factory=list)
    system_prompt: str | None = None
    model: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AIProviderTokenCountRequest:
    text: str
    model: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AIProviderResponse:
    provider: str
    model: str
    text: str
    raw: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "text": self.text,
            "raw": self.raw,
            "metadata": self.metadata,
        }


@dataclass
class AIProviderJSONResponse:
    provider: str
    model: str
    data: dict[str, Any]
    raw_text: str = ""
    raw: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "data": self.data,
            "raw_text": self.raw_text,
            "raw": self.raw,
            "metadata": self.metadata,
        }


@dataclass
class AIProviderEmbeddingResponse:
    provider: str
    model: str
    embedding: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "embedding": self.embedding,
            "metadata": self.metadata,
        }


@dataclass
class AIProviderVisionResponse:
    provider: str
    model: str
    text: str
    data: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "text": self.text,
            "data": self.data,
            "raw": self.raw,
            "metadata": self.metadata,
        }


@dataclass
class AIProviderTokenCountResponse:
    provider: str
    model: str
    input_tokens: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "input_tokens": self.input_tokens,
            "metadata": self.metadata,
        }