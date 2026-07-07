from __future__ import annotations

from typing import Any

from app.ai.providers.health import AIProviderHealthChecker


class AIProviderHealthService:
    def __init__(self):
        self.checker = AIProviderHealthChecker()

    def run(self) -> dict[str, Any]:
        return self.checker.check_all()