from __future__ import annotations

from typing import Any

from app.ai.runtime.ai_context import AIContext
from app.ai.runtime.ai_result import AIResult


class AIRuntime:
    def run_engine(
        self,
        key: str,
        engine: Any,
        context: AIContext,
    ) -> AIResult:
        raw_result = engine.run(context)

        if hasattr(raw_result, "to_dict"):
            result_data = raw_result.to_dict()
        elif isinstance(raw_result, dict):
            result_data = raw_result
        else:
            result_data = {"value": raw_result}

        return AIResult(
            production_id=context.production_id,
            key=key,
            data=result_data,
            metadata={
                "engine": getattr(engine, "engine_name", engine.__class__.__name__),
            },
        )