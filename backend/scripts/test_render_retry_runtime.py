from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from app.render.execution import (
    build_render_architecture_runtime,
)
from app.render.execution.recovery import (
    RenderRecoveryRuntime,
    RenderRetryPolicy,
)
from app.render.ffmpeg.execution import (
    FFmpegCommand,
    FFmpegExecutionIssue,
    FFmpegExecutionResult,
)
from scripts.test_render_architecture_runtime import (
    load_execution_timeline,
)


class FakePipelineResult:
    def __init__(self, execution_result):
        self.execution_result = execution_result


class RetryOncePipeline:
    def __init__(self):
        self.call_count = 0

    def render(
        self,
        context,
        progress_callback=None,
    ):
        self.call_count += 1

        success = self.call_count >= 2

        output_path = (
            Path(context.output_directory)
            / "final.mp4"
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if success:
            output_path.write_bytes(
                b"fake-success-output"
            )

        result = FFmpegExecutionResult(
            production_id=(
                context.production_id
            ),
            success=success,
            returncode=0 if success else 1,
            output_path=str(output_path),
            command=FFmpegCommand(
                binary="ffmpeg",
                arguments=[],
                output_path=str(output_path),
                duration=18.0,
            ),
            started_at=(
                "2026-01-01T00:00:00+00:00"
            ),
            finished_at=(
                "2026-01-01T00:00:01+00:00"
            ),
            duration_seconds=1.0,
            progress_events=[],
            issues=(
                []
                if success
                else [
                    FFmpegExecutionIssue(
                        level="error",
                        code=(
                            "ffmpeg_nonzero_exit"
                        ),
                        message="temporary failure",
                    )
                ]
            ),
        )

        return FakePipelineResult(result)


def main() -> None:
    execution = load_execution_timeline(
        Path(
            "storage/demo_outputs/"
            "execution_timeline.json"
        )
    )

    context = (
        build_render_architecture_runtime()
        .build_context(
            execution_timeline=execution,
            storage_root=(
                "storage/render_retry_test"
            ),
        )
    )

    pipeline = RetryOncePipeline()

    runtime = RenderRecoveryRuntime(
        pipeline=pipeline,
        retry_policy=RenderRetryPolicy(
            max_attempts=3,
            base_delay_seconds=0.0,
        ),
    )

    result = runtime.render_with_recovery(
        context=context,
    )

    print("=== Render Retry Runtime ===")
    print("success:", result.success)
    print(
        "attempt_count:",
        result.attempt_count,
    )
    print(
        "final_output_path:",
        result.final_output_path,
    )
    print(
        "diagnostics_path:",
        result.diagnostics_path,
    )

    assert result.success is True
    assert result.attempt_count == 2
    assert pipeline.call_count == 2
    assert result.attempts[0].success is False
    assert result.attempts[1].success is True

    assert result.diagnostics_path
    assert Path(
        result.diagnostics_path
    ).exists()

    print(
        "\nDONE: Render retry runtime test "
        "completed."
    )


if __name__ == "__main__":
    main()