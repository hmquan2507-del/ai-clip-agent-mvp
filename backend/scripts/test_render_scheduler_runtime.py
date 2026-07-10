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

    architecture_runtime = (
        build_render_architecture_runtime()
    )

    context = architecture_runtime.build_context(
        execution_timeline=execution,
    )

    scheduler_runtime = (
        build_render_scheduler_runtime()
    )

    plan = scheduler_runtime.schedule(context)

    output_path = Path(
        "storage/demo_outputs/"
        "render_execution_plan.json"
    )

    output_path.write_text(
        json.dumps(
            plan.to_dict(),
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    print("=== Render Execution Plan ===")
    print("production_id:", plan.production_id)
    print("version:", plan.version)
    print("node_count:", len(plan.nodes))
    print(
        "execution_level_count:",
        len(plan.levels),
    )
    print(
        "parallel_group_count:",
        plan.metadata["parallel_group_count"],
    )
    print(
        "initial_ready_nodes:",
        [
            node.node_id
            for node in plan.nodes
            if (
                node.status.value
                if hasattr(node.status, "value")
                else str(node.status)
            )
            == RenderNodeStatus.READY.value
        ],
    )
    print(
        "execution_order:",
        plan.execution_order,
    )
    print("levels:", plan.levels)
    print("issue_count:", len(plan.issues))
    print("output:", output_path)

    assert plan.metadata["scheduled"] is True
    assert len(plan.issues) == 0
    assert len(plan.nodes) == len(
        context.graph.nodes
    )
    assert len(plan.execution_order) == len(
        context.graph.nodes
    )
    assert len(set(plan.execution_order)) == len(
        plan.execution_order
    )

    order_index = {
        node_id: index
        for index, node_id in enumerate(
            plan.execution_order
        )
    }

    for node in context.graph.nodes:
        for dependency in node.dependencies:
            assert (
                order_index[dependency]
                < order_index[node.node_id]
            )

    scheduler = scheduler_runtime.scheduler

    initial_ready = scheduler.ready_nodes(plan)

    assert [
        node.node_id
        for node in initial_ready
    ] == ["prepare_inputs"]

    scheduler.mark_running(
        plan=plan,
        node_id="prepare_inputs",
    )

    scheduler.mark_completed(
        plan=plan,
        node_id="prepare_inputs",
    )

    ready_after_prepare = {
        node.node_id
        for node in scheduler.ready_nodes(plan)
    }

    assert ready_after_prepare == {
        "decode_video",
        "decode_audio",
    }

    failure_plan = scheduler_runtime.schedule(
        context
    )

    scheduler.mark_running(
        plan=failure_plan,
        node_id="prepare_inputs",
    )

    scheduler.mark_failed(
        plan=failure_plan,
        node_id="prepare_inputs",
        error="test_failure",
    )

    failed_statuses = {
        node.node_id: (
            node.status.value
            if hasattr(node.status, "value")
            else str(node.status)
        )
        for node in failure_plan.nodes
    }

    assert failed_statuses[
        "prepare_inputs"
    ] == RenderNodeStatus.FAILED.value

    assert all(
        status
        in {
            RenderNodeStatus.FAILED.value,
            RenderNodeStatus.SKIPPED.value,
        }
        for status in failed_statuses.values()
    )

    print(
        "\nDONE: Render scheduler runtime test "
        "completed."
    )


if __name__ == "__main__":
    main()