from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any

from app.media.validation import MediaValidationRuntime
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
from app.render.execution.recovery import (
    RenderRecoveryRuntime,
)


class FFmpegEncodeNodeExecutor(
    BaseRenderNodeExecutor
):
    def __init__(
        self,
        recovery_runtime: RenderRecoveryRuntime | None = None,
        media_validator: MediaValidationRuntime | None = None,
    ):
        self.recovery_runtime = (
            recovery_runtime
            or RenderRecoveryRuntime()
        )

        self.media_validator = (
            media_validator
            or MediaValidationRuntime()
        )

    def supports(
        self,
        node: RenderNode,
    ) -> bool:
        node_type = self._value(
            node.node_type
        )

        return (
            node_type
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
        current_progress = 0.0

        def on_progress(event: Any) -> None:
            nonlocal current_progress

            event_progress = self._float_or_zero(
                getattr(
                    event,
                    "progress",
                    0.0,
                )
            )

            # FFmpeg đôi khi phát payload progress trở về 0
            # trong giai đoạn mux/finalize. Không cho UI bị tụt.
            current_progress = max(
                current_progress,
                event_progress,
            )

            progress_values.append(
                round(current_progress, 2)
            )

            context.runtime_state.metadata = {
                **context.runtime_state.metadata,
                "ffmpeg_progress": round(
                    current_progress,
                    2,
                ),
            }

        try:
            recovery_result = (
                self.recovery_runtime
                .render_with_recovery(
                    context=context,
                    progress_callback=on_progress,
                )
            )

            context.runtime_state.metadata = {
                **context.runtime_state.metadata,
                "render_recovery_result": (
                    recovery_result.to_dict()
                ),
            }

            if not recovery_result.success:
                raise RuntimeError(
                    "FFmpeg render failed after recovery. "
                    f"Attempts={recovery_result.attempt_count}, "
                    f"error={recovery_result.final_error}"
                )

            output_path = (
                recovery_result.final_output_path
            )

            if not output_path:
                raise RuntimeError(
                    "Recovery runtime completed without "
                    "a final output path."
                )

            validation = (
                self.media_validator.validate(
                    local_path=output_path,
                    require_video=True,
                )
            )

            if not validation.valid:
                raise RuntimeError(
                    "Recovered render output failed "
                    "media validation. "
                    f"errors={validation.errors}"
                )

            output_file = Path(output_path)

            if (
                not output_file.exists()
                or not output_file.is_file()
            ):
                raise RuntimeError(
                    "Recovered render output does not exist: "
                    f"{output_path}"
                )

            if output_file.stat().st_size <= 0:
                raise RuntimeError(
                    "Recovered render output is empty: "
                    f"{output_path}"
                )

            ffmpeg_execution_payload = (
                self._resolve_execution_payload(
                    context=context,
                    output_path=output_path,
                    validation=validation,
                    started_at=started_at,
                    duration_seconds=round(
                        perf_counter()
                        - started_counter,
                        6,
                    ),
                    progress_values=progress_values,
                )
            )

            # WriteArtifactsNodeExecutor của Sprint 15.7
            # đọc payload này để tạo final artifact,
            # thumbnail và render report.
            context.runtime_state.metadata = {
                **context.runtime_state.metadata,
                "ffmpeg_execution_result": (
                    ffmpeg_execution_payload
                ),
                "ffmpeg_progress": 100.0,
            }

            if (
                not progress_values
                or progress_values[-1] < 100.0
            ):
                progress_values.append(100.0)

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
                    "output_path": output_path,
                    "output_file_size": (
                        output_file.stat().st_size
                    ),
                    "output_duration": (
                        validation.duration
                    ),
                    "output_width": (
                        validation.width
                    ),
                    "output_height": (
                        validation.height
                    ),
                    "output_fps": validation.fps,
                    "video_codec": (
                        validation.video_codec
                    ),
                    "audio_codec": (
                        validation.audio_codec
                    ),
                    "attempt_count": (
                        recovery_result.attempt_count
                    ),
                    "diagnostics_path": (
                        recovery_result.diagnostics_path
                    ),
                    "progress_event_count": len(
                        progress_values
                    ),
                },
                metadata={
                    "executor": (
                        self.__class__.__name__
                    ),
                    "mock": False,
                    "recovery_enabled": True,
                    "attempt_count": (
                        recovery_result.attempt_count
                    ),
                    "progress_values": (
                        progress_values
                    ),
                },
            )

        except Exception as error:
            context.runtime_state.metadata = {
                **context.runtime_state.metadata,
                "ffmpeg_encode_error": str(error),
            }

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
                    "recovery_enabled": True,
                    "progress_values": (
                        progress_values
                    ),
                },
            )

    def _resolve_execution_payload(
        self,
        context: RenderContext,
        output_path: str,
        validation: Any,
        started_at: str,
        duration_seconds: float,
        progress_values: list[float],
    ) -> dict[str, Any]:
        existing_payload = (
            context.runtime_state.metadata.get(
                "ffmpeg_execution_result"
            )
        )

        if isinstance(existing_payload, dict):
            return {
                **existing_payload,
                "success": True,
                "output_path": output_path,
                "output_file_size": (
                    Path(output_path).stat().st_size
                ),
                "output_duration": (
                    validation.duration
                ),
                "output_width": validation.width,
                "output_height": validation.height,
                "output_fps": validation.fps,
                "output_video_codec": (
                    validation.video_codec
                ),
                "output_audio_codec": (
                    validation.audio_codec
                ),
            }

        # Fallback để không làm hỏng Artifact Store nếu
        # RecoveryRuntime chưa lưu full FFmpegExecutionResult.
        return {
            "production_id": (
                context.production_id
            ),
            "success": True,
            "returncode": 0,
            "output_path": output_path,
            "command": {
                "binary": "ffmpeg",
                "arguments": [],
                "command": ["ffmpeg"],
                "output_path": output_path,
                "duration": (
                    validation.duration
                    or context.execution_timeline.duration
                ),
                "metadata": {
                    "source": (
                        "render_recovery_runtime"
                    ),
                    "reconstructed": True,
                },
            },
            "started_at": started_at,
            "finished_at": self._now(),
            "duration_seconds": duration_seconds,
            "progress_events": [
                {
                    "progress": value,
                    "out_time_seconds": 0.0,
                    "speed": None,
                    "frame": None,
                    "fps": None,
                    "bitrate": None,
                    "total_size": None,
                    "status": (
                        "end"
                        if value >= 100.0
                        else "continue"
                    ),
                    "metadata": {
                        "reconstructed": True,
                    },
                }
                for value in progress_values
            ],
            "issues": [],
            "stderr_tail": None,
            "output_file_size": (
                Path(output_path).stat().st_size
            ),
            "output_duration": validation.duration,
            "output_width": validation.width,
            "output_height": validation.height,
            "output_fps": validation.fps,
            "output_video_codec": (
                validation.video_codec
            ),
            "output_audio_codec": (
                validation.audio_codec
            ),
            "metadata": {
                "executor": (
                    self.__class__.__name__
                ),
                "recovery_enabled": True,
                "reconstructed_execution_payload": True,
            },
        }

    def _value(
        self,
        value: Any,
    ) -> str:
        return (
            value.value
            if hasattr(value, "value")
            else str(value)
        )

    def _float_or_zero(
        self,
        value: Any,
    ) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _now(self) -> str:
        return datetime.now(
            timezone.utc
        ).isoformat()