from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

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


class MockRenderNodeExecutor(BaseRenderNodeExecutor):
    supported_node_types: set[str] = set()

    def __init__(
        self,
        delay_seconds: float = 0.01,
        fail_node_ids: set[str] | None = None,
    ):
        self.delay_seconds = max(0.0, delay_seconds)
        self.fail_node_ids = fail_node_ids or set()

    def supports(
        self,
        node: RenderNode,
    ) -> bool:
        return self._value(node.node_type) in self.supported_node_types

    def execute(
        self,
        context: RenderContext,
        node: RenderNode,
    ) -> RenderNodeExecutionResult:
        started_at = self._now()
        started_counter = time.perf_counter()

        try:
            if node.node_id in self.fail_node_ids:
                raise RuntimeError(
                    f"Mock execution failure: {node.node_id}"
                )

            if self.delay_seconds > 0:
                time.sleep(self.delay_seconds)

            outputs = self.build_outputs(
                context=context,
                node=node,
            )

            finished_at = self._now()

            return RenderNodeExecutionResult(
                node_id=node.node_id,
                status=RenderNodeStatus.COMPLETED,
                started_at=started_at,
                finished_at=finished_at,
                duration_seconds=round(
                    time.perf_counter() - started_counter,
                    6,
                ),
                outputs=outputs,
                metadata={
                    "executor": self.__class__.__name__,
                    "mock": True,
                },
            )

        except Exception as error:
            finished_at = self._now()

            return RenderNodeExecutionResult(
                node_id=node.node_id,
                status=RenderNodeStatus.FAILED,
                started_at=started_at,
                finished_at=finished_at,
                duration_seconds=round(
                    time.perf_counter() - started_counter,
                    6,
                ),
                outputs={},
                error=str(error),
                metadata={
                    "executor": self.__class__.__name__,
                    "mock": True,
                },
            )

    def build_outputs(
        self,
        context: RenderContext,
        node: RenderNode,
    ) -> dict[str, Any]:
        return {
            "node_id": node.node_id,
            "node_type": self._value(node.node_type),
            "status": "mock_completed",
        }

    def _value(self, value: Any) -> str:
        return value.value if hasattr(value, "value") else str(value)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()


class PrepareInputsExecutor(MockRenderNodeExecutor):
    supported_node_types = {
        RenderNodeType.PREPARE_INPUTS.value,
    }

    def build_outputs(
        self,
        context: RenderContext,
        node: RenderNode,
    ) -> dict[str, Any]:
        return {
            "prepared_input_count": len(
                context.execution_timeline.inputs
            ),
        }


class DecodeExecutor(MockRenderNodeExecutor):
    supported_node_types = {
        RenderNodeType.DECODE_VIDEO.value,
        RenderNodeType.DECODE_AUDIO.value,
    }


class ComposeVideoExecutor(MockRenderNodeExecutor):
    supported_node_types = {
        RenderNodeType.COMPOSE_PRIMARY_VIDEO.value,
    }


class OverlayExecutor(MockRenderNodeExecutor):
    supported_node_types = {
        RenderNodeType.OVERLAY_BROLL.value,
    }


class EffectExecutor(MockRenderNodeExecutor):
    supported_node_types = {
        RenderNodeType.APPLY_EFFECTS.value,
        RenderNodeType.APPLY_TRANSITIONS.value,
    }


class SubtitleExecutor(MockRenderNodeExecutor):
    supported_node_types = {
        RenderNodeType.DRAW_SUBTITLES.value,
    }


class AudioMixExecutor(MockRenderNodeExecutor):
    supported_node_types = {
        RenderNodeType.MIX_AUDIO.value,
    }


class EncodeExecutor(MockRenderNodeExecutor):
    supported_node_types = {
        RenderNodeType.ENCODE_VIDEO.value,
    }

    def build_outputs(
        self,
        context: RenderContext,
        node: RenderNode,
    ) -> dict[str, Any]:
        return {
            "mock_encoded_path": (
                f"{context.temp_directory}/mock_encoded.mp4"
            ),
        }


class ArtifactExecutor(MockRenderNodeExecutor):
    supported_node_types = {
        RenderNodeType.WRITE_ARTIFACTS.value,
    }

    def build_outputs(
        self,
        context: RenderContext,
        node: RenderNode,
    ) -> dict[str, Any]:
        return {
            "mock_final_path": (
                f"{context.output_directory}/final.mp4"
            ),
        }