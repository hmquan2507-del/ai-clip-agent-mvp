from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter

from app.render.execution.artifact import (
    RenderArtifactStore,
)
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
from app.render.ffmpeg.execution.models import (
    FFmpegCommand,
    FFmpegExecutionResult,
)


class WriteArtifactsNodeExecutor(
    BaseRenderNodeExecutor
):
    def __init__(
        self,
        artifact_store: RenderArtifactStore | None = None,
    ):
        self.artifact_store = (
            artifact_store or RenderArtifactStore()
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
            == RenderNodeType.WRITE_ARTIFACTS.value
        )

    def execute(
        self,
        context: RenderContext,
        node: RenderNode,
    ) -> RenderNodeExecutionResult:
        started_at = self._now()
        started_counter = perf_counter()

        try:
            payload = (
                context.runtime_state.metadata.get(
                    "ffmpeg_execution_result"
                )
            )

            if not isinstance(payload, dict):
                raise RuntimeError(
                    "FFmpeg execution result was not found "
                    "in render runtime state."
                )

            execution_result = self._hydrate_result(
                payload
            )

            store_result = self.artifact_store.store(
                context=context,
                execution_result=execution_result,
                generate_thumbnail=(
                    context.render_config.generate_thumbnail
                ),
                generate_report=(
                    context.render_config.generate_report
                ),
            )

            if not store_result.success:
                raise RuntimeError(
                    "Render artifact store failed. "
                    f"Issues={len(store_result.issues)}"
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
                    "artifact_count": len(
                        store_result.artifacts
                    ),
                    "manifest_path": (
                        store_result.manifest_path
                    ),
                    "artifacts": [
                        item.to_dict()
                        for item
                        in store_result.artifacts
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

    def _hydrate_result(
        self,
        payload: dict,
    ) -> FFmpegExecutionResult:
        command_payload = (
            payload.get("command") or {}
        )

        command = FFmpegCommand(
            binary=command_payload.get(
                "binary",
                "ffmpeg",
            ),
            arguments=list(
                command_payload.get(
                    "arguments",
                    [],
                )
            ),
            output_path=command_payload.get(
                "output_path",
                payload.get("output_path", ""),
            ),
            duration=float(
                command_payload.get(
                    "duration",
                    0.0,
                )
                or 0.0
            ),
            metadata=command_payload.get(
                "metadata"
            ) or {},
        )

        return FFmpegExecutionResult(
            production_id=payload["production_id"],
            success=bool(payload["success"]),
            returncode=payload.get("returncode"),
            output_path=payload["output_path"],
            command=command,
            started_at=payload["started_at"],
            finished_at=payload["finished_at"],
            duration_seconds=float(
                payload.get(
                    "duration_seconds",
                    0.0,
                )
            ),
            progress_events=[],
            issues=[],
            stderr_tail=payload.get(
                "stderr_tail"
            ),
            output_file_size=payload.get(
                "output_file_size"
            ),
            output_duration=payload.get(
                "output_duration"
            ),
            output_width=payload.get(
                "output_width"
            ),
            output_height=payload.get(
                "output_height"
            ),
            output_fps=payload.get(
                "output_fps"
            ),
            output_video_codec=payload.get(
                "output_video_codec"
            ),
            output_audio_codec=payload.get(
                "output_audio_codec"
            ),
            metadata=payload.get("metadata") or {},
        )

    def _now(self) -> str:
        return datetime.now(
            timezone.utc
        ).isoformat()