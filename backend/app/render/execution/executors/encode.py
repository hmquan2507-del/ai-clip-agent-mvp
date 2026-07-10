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
from app.render.ffmpeg.execution import (
    FFmpegRenderPipeline,
)


class FFmpegEncodeNodeExecutor(
    BaseRenderNodeExecutor
):
    def __init__(
        self,
        pipeline: FFmpegRenderPipeline | None = None,
    ):
        self.pipeline = (
            pipeline or FFmpegRenderPipeline()
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
            == RenderNodeType.ENCODE_VIDEO.value
        )

    def execute(
        self,
        context: RenderContext,
        node: RenderNode,
    ) -> RenderNodeExecutionResult:
        started_at = self._now()
        started_counter = perf_counter()

        progress_values: list[float] = []

        try:
            pipeline_result = self.pipeline.render(
                context=context,
                progress_callback=lambda event: (
                    progress_values.append(
                        event.progress
                    )
                ),
            )

            execution_result = (
                pipeline_result.execution_result
            )

            if not execution_result.success:
                raise RuntimeError(
                    "FFmpeg render execution failed. "
                    f"Issues={len(execution_result.issues)}"
                )

            context.runtime_state.metadata = {
                **context.runtime_state.metadata,
                "ffmpeg_execution_result": (
                    execution_result.to_dict()
                ),
            }

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
                    "output_path": (
                        execution_result.output_path
                    ),
                    "output_file_size": (
                        execution_result.output_file_size
                    ),
                    "output_duration": (
                        execution_result.output_duration
                    ),
                    "output_width": (
                        execution_result.output_width
                    ),
                    "output_height": (
                        execution_result.output_height
                    ),
                    "output_fps": (
                        execution_result.output_fps
                    ),
                    "video_codec": (
                        execution_result.output_video_codec
                    ),
                    "audio_codec": (
                        execution_result.output_audio_codec
                    ),
                    "progress_event_count": len(
                        execution_result.progress_events
                    ),
                },
                metadata={
                    "executor": (
                        self.__class__.__name__
                    ),
                    "mock": False,
                    "progress_values": (
                        progress_values
                    ),
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