from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from app.render.execution import (
    RenderNodeStatus,
    build_render_architecture_runtime,
    build_render_execution_runtime,
    build_render_scheduler_runtime,
)
from scripts.test_render_architecture_runtime import (
    load_execution_timeline,
)


def main() -> None:
    input_path = Path(
        "storage/demo_outputs/execution_timeline.json"
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
        )
    )

    plan = build_render_scheduler_runtime().schedule(
        context
    )

    runtime = build_render_execution_runtime(
        delay_seconds=0.001,
    )

    summary = runtime.run(
        context=context,
        plan=plan,
    )

    output_path = Path(
        "storage/demo_outputs/"
        "render_execution_runtime.json"
    )

    output_path.write_text(
        json.dumps(
            summary.to_dict(),
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    print("=== Render Execution Runtime ===")
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
    print("event_count:", len(summary.events))
    print(
        "executed_nodes:",
        [
            item.node_id
            for item in summary.node_results
        ],
    )
    print("output:", output_path)

    assert summary.success is True
    assert summary.completed_node_count == 11
    assert summary.failed_node_count == 0
    assert summary.skipped_node_count == 0
    assert summary.progress == 100.0
    assert len(summary.node_results) == 11

    assert [
        item.node_id
        for item in summary.node_results
    ] == plan.execution_order

    assert summary.events[0].event_type == "START"
    assert summary.events[-1].event_type == "FINISHED"

    failure_context = (
        build_render_architecture_runtime()
        .build_context(
            execution_timeline=execution,
            storage_root=(
                "storage/render_failure_test"
            ),
        )
    )

    failure_plan = (
        build_render_scheduler_runtime().schedule(
            failure_context
        )
    )

    failure_runtime = (
        build_render_execution_runtime(
            delay_seconds=0.0,
            fail_node_ids={"overlay_broll"},
        )
    )

    failure_summary = failure_runtime.run(
        context=failure_context,
        plan=failure_plan,
    )

    print("\n=== Failure Propagation ===")
    print("success:", failure_summary.success)
    print(
        "completed_node_count:",
        failure_summary.completed_node_count,
    )
    print(
        "failed_node_count:",
        failure_summary.failed_node_count,
    )
    print(
        "skipped_node_count:",
        failure_summary.skipped_node_count,
    )
    print(
        "failed_node_id:",
        failure_summary.failed_node_id,
    )

    assert failure_summary.success is False
    assert failure_summary.failed_node_count == 1
    assert failure_summary.failed_node_id == (
        "overlay_broll"
    )
    assert failure_summary.skipped_node_count > 0

    failed_statuses = {
        node.node_id: (
            node.status.value
            if hasattr(node.status, "value")
            else str(node.status)
        )
        for node in failure_plan.nodes
    }

    assert failed_statuses[
        "overlay_broll"
    ] == RenderNodeStatus.FAILED.value

    assert failed_statuses[
        "encode_video"
    ] == RenderNodeStatus.SKIPPED.value

    assert failed_statuses[
        "write_artifacts"
    ] == RenderNodeStatus.SKIPPED.value

    print(
        "\nDONE: Render execution runtime test "
        "completed."
    )


if __name__ == "__main__":
    main()