from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from app.render.production import (
    build_production_render_runtime,
)
from scripts.test_render_architecture_runtime import (
    load_execution_timeline,
)


def main() -> None:
    execution_path = Path(
        "storage/demo_outputs/"
        "execution_timeline.json"
    )

    if not execution_path.exists():
        raise RuntimeError(
            "Run test_timeline_compiler_runtime.py first."
        )

    execution_timeline = (
        load_execution_timeline(
            execution_path
        )
    )

    storage_root = (
        "storage/render_end_to_end_demo"
    )

    runtime = (
        build_production_render_runtime()
    )

    result = runtime.render(
        execution_timeline=execution_timeline,
        storage_root=storage_root,
    )

    output_path = Path(
        "storage/demo_outputs/"
        "render_end_to_end_result.json"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            result.to_dict(),
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    print(
        "=== Render End-to-End Production Demo ==="
    )
    print(
        "production_id:",
        result.production_id,
    )
    print("version:", result.version)
    print("success:", result.success)

    print(
        "completed_node_count:",
        (
            result.execution_summary
            .completed_node_count
            if result.execution_summary
            else None
        ),
    )

    print(
        "failed_node_count:",
        (
            result.execution_summary
            .failed_node_count
            if result.execution_summary
            else None
        ),
    )

    print(
        "skipped_node_count:",
        (
            result.execution_summary
            .skipped_node_count
            if result.execution_summary
            else None
        ),
    )

    print(
        "quality_status:",
        (
            result.quality_report.status
            if result.quality_report
            else None
        ),
    )

    print(
        "quality_score:",
        (
            result.quality_report.quality_score
            if result.quality_report
            else None
        ),
    )

    print(
        "final_video_path:",
        result.final_video_path,
    )
    print(
        "thumbnail_path:",
        result.thumbnail_path,
    )
    print(
        "render_report_path:",
        result.render_report_path,
    )
    print(
        "artifact_manifest_path:",
        result.artifact_manifest_path,
    )
    print(
        "quality_report_path:",
        result.quality_report_path,
    )
    print(
        "recovery_diagnostics_path:",
        result.recovery_diagnostics_path,
    )
    print(
        "issue_count:",
        len(result.issues),
    )
    print("output:", output_path)

    if result.issues:
        print("\n=== Issues ===")

        for issue in result.issues:
            print(issue.to_dict())

    assert result.success is True
    assert result.execution_summary is not None
    assert (
        result.execution_summary
        .completed_node_count
        == 11
    )
    assert (
        result.execution_summary
        .failed_node_count
        == 0
    )
    assert (
        result.execution_summary
        .skipped_node_count
        == 0
    )

    assert result.quality_report is not None
    assert result.quality_report.approved is True
    assert (
        result.quality_report.failure_count
        == 0
    )

    required_paths = [
        result.final_video_path,
        result.thumbnail_path,
        result.render_report_path,
        result.artifact_manifest_path,
        result.quality_report_path,
        result.recovery_diagnostics_path,
    ]

    for value in required_paths:
        assert value

        path = Path(value)

        assert path.exists()
        assert path.is_file()
        assert path.stat().st_size > 0

    assert len(result.issues) == 0

    print(
        "\nDONE: Render end-to-end production "
        "demo completed."
    )


if __name__ == "__main__":
    main()