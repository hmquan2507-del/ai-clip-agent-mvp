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
from app.timeline.compiler.models import (
    ExecutionTimeline,
    TimelineCompilerIssue,
    TimelineInput,
    TimelineInstruction,
)


def load_execution_timeline(
    path: Path,
) -> ExecutionTimeline:
    payload = json.loads(
        path.read_text(encoding="utf-8")
    )

    canvas = payload["canvas"]

    return ExecutionTimeline(
        production_id=payload["production_id"],
        version=payload["version"],
        duration=payload["duration"],
        width=canvas["width"],
        height=canvas["height"],
        fps=canvas["fps"],
        inputs=[
            TimelineInput(
                input_id=item["input_id"],
                input_type=item["input_type"],
                local_path=item["local_path"],
                asset_id=item.get("asset_id"),
                metadata=item.get("metadata") or {},
            )
            for item in payload["inputs"]
        ],
        instructions=[
            TimelineInstruction(
                instruction_id=item["instruction_id"],
                instruction_type=item[
                    "instruction_type"
                ],
                track_type=item["track_type"],
                start_time=item["start_time"],
                end_time=item["end_time"],
                layer=item["layer"],
                input_id=item.get("input_id"),
                target_id=item.get("target_id"),
                parameters=(
                    item.get("parameters") or {}
                ),
                metadata=item.get("metadata") or {},
            )
            for item in payload["instructions"]
        ],
        issues=[
            TimelineCompilerIssue(
                level=item["level"],
                code=item["code"],
                message=item["message"],
                source_id=item.get("source_id"),
                metadata=item.get("metadata") or {},
            )
            for item in payload.get("issues", [])
        ],
        metadata=payload.get("metadata") or {},
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

    runtime = build_render_architecture_runtime()

    context = runtime.build_context(
        execution_timeline=execution,
    )

    if context.graph is None:
        raise RuntimeError(
            "Render graph was not created."
        )

    output_path = Path(
        "storage/demo_outputs/render_context.json"
    )

    output_path.write_text(
        json.dumps(
            context.to_dict(),
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    graph = context.graph

    print("=== Render Architecture ===")
    print("production_id:", context.production_id)
    print("node_count:", len(graph.nodes))
    print("issue_count:", len(graph.issues))
    print("graph_valid:", graph.metadata["valid"])
    print(
        "nodes:",
        [node.node_id for node in graph.nodes],
    )
    print("output:", output_path)

    assert graph.metadata["valid"] is True
    assert len(graph.issues) == 0
    assert len(graph.nodes) >= 5

    print(
        "\nDONE: Render architecture runtime test "
        "completed."
    )


if __name__ == "__main__":
    main()