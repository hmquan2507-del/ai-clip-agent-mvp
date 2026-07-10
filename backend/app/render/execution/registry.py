from __future__ import annotations

from app.render.execution.context import RenderContext
from app.render.execution.interfaces import (
    BaseRenderNodeExecutor,
)
from app.render.execution.models import (
    RenderNode,
    RenderNodeExecutionResult,
)


class RenderNodeExecutorRegistry:
    def __init__(
        self,
        executors: list[BaseRenderNodeExecutor] | None = None,
    ):
        self._executors: list[
            BaseRenderNodeExecutor
        ] = []

        for executor in executors or []:
            self.register(executor)

    def register(
        self,
        executor: BaseRenderNodeExecutor,
    ) -> None:
        if executor in self._executors:
            return

        self._executors.append(executor)

    def find_executor(
        self,
        node: RenderNode,
    ) -> BaseRenderNodeExecutor:
        matches = [
            executor
            for executor in self._executors
            if executor.supports(node)
        ]

        if not matches:
            raise LookupError(
                "No render node executor registered for "
                f"node={node.node_id}, "
                f"type={self._value(node.node_type)}"
            )

        if len(matches) > 1:
            raise RuntimeError(
                "Multiple render node executors support "
                f"node={node.node_id}, "
                f"type={self._value(node.node_type)}"
            )

        return matches[0]

    def execute_node(
        self,
        context: RenderContext,
        node: RenderNode,
    ) -> RenderNodeExecutionResult:
        executor = self.find_executor(node)

        return executor.execute(
            context=context,
            node=node,
        )

    def count(self) -> int:
        return len(self._executors)

    def _value(self, value) -> str:
        return value.value if hasattr(value, "value") else str(value)