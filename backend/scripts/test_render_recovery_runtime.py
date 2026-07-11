from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from app.render.execution import (
    build_render_architecture_runtime,
)
from app.render.execution.recovery import (
    RenderCleanupMode,
    RenderRetryPolicy,
    build_render_cleanup_runtime,
    build_render_failure_classifier,
)
from app.render.ffmpeg.execution import (
    FFmpegCommand,
    FFmpegExecutionIssue,
    FFmpegExecutionResult,
)
from scripts.test_render_architecture_runtime import (
    load_execution_timeline,
)


def fake_result(
    issue_code: str,
    stderr: str | None = None,
    returncode: int = 1,
) -> FFmpegExecutionResult:
    return FFmpegExecutionResult(
        production_id="test",
        success=False,
        returncode=returncode,
        output_path=(
            "storage/render_recovery_test/"
            "output/final.mp4"
        ),
        command=FFmpegCommand(
            binary="ffmpeg",
            arguments=[],
            output_path=(
                "storage/render_recovery_test/"
                "output/final.mp4"
            ),
            duration=18.0,
        ),
        started_at="2026-01-01T00:00:00+00:00",
        finished_at="2026-01-01T00:00:01+00:00",
        duration_seconds=1.0,
        progress_events=[],
        issues=[
            FFmpegExecutionIssue(
                level="error",
                code=issue_code,
                message=issue_code,
            )
        ],
        stderr_tail=stderr,
    )


def main() -> None:
    execution_path = Path(
        "storage/demo_outputs/"
        "execution_timeline.json"
    )

    execution = load_execution_timeline(
        execution_path
    )

    context = (
        build_render_architecture_runtime()
        .build_context(
            execution_timeline=execution,
            storage_root=(
                "storage/render_recovery_test"
            ),
        )
    )

    classifier = (
        build_render_failure_classifier()
    )

    policy = RenderRetryPolicy(
        max_attempts=3,
        base_delay_seconds=0.0,
    )

    timeout_classification = (
        classifier.classify(
            result=fake_result(
                "ffmpeg_timeout"
            ),
            policy=policy,
            attempt_number=1,
        )
    )

    process_classification = (
        classifier.classify(
            result=fake_result(
                "ffmpeg_nonzero_exit"
            ),
            policy=policy,
            attempt_number=1,
        )
    )

    missing_binary_classification = (
        classifier.classify(
            result=fake_result(
                "ffmpeg_not_installed"
            ),
            policy=policy,
            attempt_number=1,
        )
    )

    print("=== Failure Classification ===")
    print(
        "timeout:",
        timeout_classification.to_dict(),
    )
    print(
        "process:",
        process_classification.to_dict(),
    )
    print(
        "missing_binary:",
        missing_binary_classification.to_dict(),
    )

    assert (
        timeout_classification.to_dict()[
            "retry_decision"
        ]
        == "retry_after_cleanup"
    )

    assert (
        process_classification.to_dict()[
            "retry_decision"
        ]
        == "retry_after_cleanup"
    )

    assert (
        missing_binary_classification.to_dict()[
            "retry_decision"
        ]
        == "do_not_retry"
    )

    output_path = (
        Path(context.output_directory)
        / "final.mp4"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_bytes(
        b"partial-render"
    )

    cleanup = (
        build_render_cleanup_runtime()
        .cleanup(
            context=context,
            mode=RenderCleanupMode.PARTIAL,
        )
    )

    print("\n=== Cleanup ===")
    print(cleanup.to_dict())

    assert cleanup.success is True
    assert not output_path.exists()
    assert str(output_path) in (
        cleanup.removed_paths
    )

    report_path = Path(
        "storage/demo_outputs/"
        "render_recovery_test_result.json"
    )

    report_path.write_text(
        json.dumps(
            {
                "timeout": (
                    timeout_classification.to_dict()
                ),
                "process": (
                    process_classification.to_dict()
                ),
                "missing_binary": (
                    missing_binary_classification.to_dict()
                ),
                "cleanup": cleanup.to_dict(),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        "\nDONE: Render recovery runtime test "
        "completed."
    )


if __name__ == "__main__":
    main()