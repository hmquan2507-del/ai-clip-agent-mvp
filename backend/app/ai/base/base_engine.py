from __future__ import annotations

from abc import ABC, abstractmethod

from app.ai.runtime.ai_context import AIContext


class BaseAIEngine(ABC):
    engine_name: str = "base_ai_engine"

    @abstractmethod
    def run(self, context: AIContext):
        raise NotImplementedError