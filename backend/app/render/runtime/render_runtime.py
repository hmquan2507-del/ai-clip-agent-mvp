from __future__ import annotations

from typing import Any

from app.render.runtime.models import RenderContext, RenderRuntimeResult


class RenderRuntime:
    def run_runtime(
        self,
        key: str,
        runtime: Any,
        context: RenderContext,
        **kwargs: Any,
    ) -> RenderRuntimeResult:
        raw_result = runtime.run(
            context=context,
            **kwargs,
        )

        if isinstance(raw_result, RenderRuntimeResult):
            return raw_result

        if hasattr(raw_result, "to_dict"):
            payload = raw_result.to_dict()
        elif isinstance(raw_result, dict):
            payload = raw_result
        else:
            payload = {"value": raw_result}

        return RenderRuntimeResult(
            production_id=context.production_id,
            key=key,
            payload=payload,
            metadata={
                "runtime": getattr(
                    runtime,
                    "runtime_name",
                    runtime.__class__.__name__,
                ),
            },
        )