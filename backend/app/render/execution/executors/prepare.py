from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter

from app.render.execution.context import RenderContext
from app.render.execution.enums import (
    RenderNodeStatus,
    RenderNodeType,
)
from app.render.execution.interfaces import (
    BaseRenderNodeExecutor,
)
from app.render.execution.models import (
    RenderNode,
    RenderNodeExecutionResult,
)
from app.render.execution.preloader import (
    RenderAssetPreloader,
)


class PrepareInputsNodeExecutor(
    BaseRenderNodeExecutor
):
    def __init__(
        self,
        preloader: RenderAssetPreloader | None = None,
    ):
        self.preloader = (
            preloader or RenderAssetPreloader()
        )

    def supports(
        self,
        node: RenderNode,
    ) -> bool:
        value = (
            node.node_type.value
            if hasattr(node.node_type, "value")
            else str(node.node_type)
        )

        return (
            value
            == RenderNodeType.PREPARE_INPUTS.value
        )

    def execute(
        self,
        context: RenderContext,
        node: RenderNode,
    ) -> RenderNodeExecutionResult:
        started_at = self._now()
        started_counter = perf_counter()

        try:
            result = self.preloader.preload(
                context
            )

            if not result.success:
                raise RuntimeError(
                    "Render asset preload failed. "
                    f"Issue count={len(result.issues)}"
                )

            return RenderNodeExecutionResult(
                node_id=node.node_id,
                status=RenderNodeStatus.COMPLETED,
                started_at=started_at,
                finished_at=self._now(),
                duration_seconds=round(
                    perf_counter()
                    - started_counter,
                    6,
                ),
                outputs={
                    "manifest_path": (
                        result.manifest_path
                    ),
                    "prepared_input_count": len(
                        result.prepared_inputs
                    ),
                    "prepared_inputs": [
                        item.to_dict()
                        for item
                        in result.prepared_inputs
                    ],
                },
                metadata={
                    "executor": (
                        self.__class__.__name__
                    ),
                    "mock": False,
                },
            )

        except Exception as error:
            return RenderNodeExecutionResult(
                node_id=node.node_id,
                status=RenderNodeStatus.FAILED,
                started_at=started_at,
                finished_at=self._now(),
                duration_seconds=round(
                    perf_counter()
                    - started_counter,
                    6,
                ),
                outputs={},
                error=str(error),
                metadata={
                    "executor": (
                        self.__class__.__name__
                    ),
                    "mock": False,
                },
            )

    def _now(self) -> str:
        return datetime.now(
            timezone.utc
        ).isoformat()