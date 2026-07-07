from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AIProviderConfig:
    provider_key: str
    default_model: str
    api_key_env: str | None = None
    enabled: bool = True
    timeout_seconds: int = 60