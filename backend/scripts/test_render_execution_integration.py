from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from app.render.execution import (
    build_render_architecture_runtime,
    build_render_execution_runtime,
    build_render_scheduler_runtime,
)
from scripts.test_render_architecture_runtime import (
    load_execution_timeline,
)


def main() -> None:
    input_path = Path(
        "storage/demo_outputs/"
        "execution_timeline.json"
    )

    if not input_path.exists():
        raise RuntimeError(
            "Run test_timeline_compiler_runtime.py first."
        )

    execution = load_execution_timeline(
        input_path
    )

    context = (
        build_render_architecture_runtime()
        .build_context(
            execution_timeline=execution,
            storage_root=(
                "storage/render_execution_integration"
            ),
        )
    )

    plan = (
        build_render_scheduler_runtime()
        .schedule(context)
    )

    runtime = build_render_execution_runtime(
        delay_seconds=0.0,
    )

    summary = runtime.run(
        context=context,
        plan=plan,
    )

    output_path = Path(
        "storage/demo_outputs/"
        "render_execution_integration.json"
    )

    output_path.write_text(
        json.dumps(
            {
                "summary": summary.to_dict(),
                "context": context.to_dict(),
            },
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    print(
        "=== Render Execution Integration ==="
    )
    print("success:", summary.success)
    print(
        "completed_node_count:",
        summary.completed_node_count,
    )
    print(
        "failed_node_count:",
        summary.failed_node_count,
    )
    print(
        "skipped_node_count:",
        summary.skipped_node_count,
    )
    print("progress:", summary.progress)
    print(
        "artifact_count:",
        len(context.artifacts),
    )
    print(
        "artifact_types:",
        [
            (
                artifact.artifact_type.value
                if hasattr(
                    artifact.artifact_type,
                    "value",
                )
                else str(
                    artifact.artifact_type
                )
            )
            for artifact in context.artifacts
        ],
    )
    print("output:", output_path)

    assert summary.success is True
    assert summary.completed_node_count == 11
    assert summary.failed_node_count == 0
    assert summary.skipped_node_count == 0
    assert summary.progress == 100.0

    assert len(context.artifacts) >= 3

    artifact_ids = {
        artifact.artifact_id
        for artifact in context.artifacts
    }

    assert "final_video" in artifact_ids
    assert "thumbnail" in artifact_ids
    assert "render_report" in artifact_ids

    final_artifact = next(
        artifact
        for artifact in context.artifacts
        if artifact.artifact_id
        == "final_video"
    )

    final_path = Path(
        final_artifact.local_path
    )

    assert final_path.exists()
    assert final_path.stat().st_size > 0

    print(
        "\nDONE: Render execution integration "
        "test completed."
    )


if __name__ == "__main__":
    main()