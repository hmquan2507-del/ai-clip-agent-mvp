from __future__ import annotations

from app.ai.runtime.ai_context import AIContext
from app.ai.runtime.ai_result import AIResult
from app.ai.runtime.ai_runtime import AIRuntime
from app.ai.runtime.engine_registry import EngineRegistry


class AIPipeline:
    def __init__(
        self,
        registry: EngineRegistry,
        runtime: AIRuntime | None = None,
    ):
        self.registry = registry
        self.runtime = runtime or AIRuntime()

    def run(
        self,
        engine_keys: list[str],
        context: AIContext,
    ) -> list[AIResult]:
        results: list[AIResult] = []

        for key in engine_keys:
            engine = self.registry.get(key)

            result = self.runtime.run_engine(
                key=key,
                engine=engine,
                context=context,
            )

            context.set_runtime_result(key, result.data)
            results.append(result)

        return results