from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from app.render.execution import (
    RenderArtifact,
    build_render_architecture_runtime,
    build_render_quality_gate,
)
from scripts.test_render_architecture_runtime import (
    load_execution_timeline,
)


def main() -> None:
    execution_path = Path(
        "storage/demo_outputs/"
        "execution_timeline.json"
    )

    final_video_path = Path(
        "storage/render_execution_integration/"
        "221e4b01-5fb9-4b4a-a549-4fb32c455059/"
        "artifacts/final.mp4"
    )

    if not execution_path.exists():
        raise RuntimeError(
            "Run test_timeline_compiler_runtime.py first."
        )

    if not final_video_path.exists():
        raise RuntimeError(
            "Run test_render_execution_integration.py first."
        )

    execution = load_execution_timeline(
        execution_path
    )

    context = (
        build_render_architecture_runtime()
        .build_context(
            execution_timeline=execution,
            storage_root=(
                "storage/render_quality_test"
            ),
        )
    )

    context.artifacts = [
        RenderArtifact(
            artifact_id="final_video",
            artifact_type="final_video",
            local_path=str(final_video_path),
            mime_type="video/mp4",
            checksum=None,
            size=final_video_path.stat().st_size,
        )
    ]

    report = build_render_quality_gate().validate(
        context=context,
        output_path=str(final_video_path),
    )

    output_path = Path(
        "storage/demo_outputs/"
        "render_quality_gate_result.json"
    )

    output_path.write_text(
        json.dumps(
            report.to_dict(),
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    print("=== Render Quality Gate ===")
    print("status:", report.status)
    print(
        "quality_score:",
        report.quality_score,
    )
    print("approved:", report.approved)
    print(
        "warning_count:",
        report.warning_count,
    )
    print(
        "failure_count:",
        report.failure_count,
    )
    print("report:", report.report_path)

    print("\n=== Checks ===")

    for check in report.checks:
        print(
            check.to_dict()
        )

    assert report.failure_count == 0
    assert report.approved is True
    assert report.quality_score >= 70.0

    assert report.report_path
    assert Path(
        report.report_path
    ).exists()

    check_types = {
        (
            item.check_type.value
            if hasattr(
                item.check_type,
                "value",
            )
            else str(item.check_type)
        )
        for item in report.checks
    }

    assert "media_validation" in check_types
    assert "file_integrity" in check_types
    assert "duration" in check_types
    assert "resolution" in check_types
    assert "fps" in check_types
    assert "black_frame" in check_types
    assert "silence" in check_types
    assert "artifact_integrity" in check_types

    print(
        "\nDONE: Render quality gate test "
        "completed."
    )


if __name__ == "__main__":
    main()