from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from app.render.execution import (
    build_render_architecture_runtime,
    build_render_asset_preloader,
)
from app.render.ffmpeg import (
    build_ffmpeg_filtergraph_builder,
    build_ffmpeg_filtergraph_validator,
    build_ffmpeg_instruction_compiler,
    build_ffmpeg_instruction_plan_validator,
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
                "storage/ffmpeg_filtergraph_test"
            ),
        )
    )

    preload_result = (
        build_render_asset_preloader().preload(
            context
        )
    )

    if not preload_result.success:
        raise RuntimeError(
            "Asset preload failed."
        )

    instruction_plan = (
        build_ffmpeg_instruction_compiler()
        .compile(
            context=context,
            preload_result=preload_result,
        )
    )

    instruction_plan = (
        build_ffmpeg_instruction_plan_validator()
        .validate(instruction_plan)
    )

    assert instruction_plan.metadata["valid"] is True

    graph = (
        build_ffmpeg_filtergraph_builder()
        .build(instruction_plan)
    )

    validator = (
        build_ffmpeg_filtergraph_validator()
    )

    graph = validator.validate_contract(
        graph
    )

    output_path = Path(
        "storage/demo_outputs/"
        "ffmpeg_filtergraph.json"
    )

    output_path.write_text(
        json.dumps(
            graph.to_dict(),
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    print("=== FFmpeg FilterGraph ===")
    print("production_id:", graph.production_id)
    print("version:", graph.version)
    print(
        "input_count:",
        len(graph.input_arguments),
    )
    print("chain_count:", len(graph.chains))
    print(
        "video_output_label:",
        graph.video_output_label,
    )
    print(
        "audio_output_label:",
        graph.audio_output_label,
    )
    print(
        "contract_valid:",
        graph.metadata["contract_valid"],
    )
    print("issue_count:", len(graph.issues))
    print("output:", output_path)

    assert graph.metadata["contract_valid"] is True
    assert len(graph.issues) == 0
    assert graph.video_output_label
    assert graph.audio_output_label
    assert graph.filter_complex
    assert "-map" in graph.map_arguments

    print(
        "\n=== Validate with FFmpeg ==="
    )

    graph = validator.validate_with_ffmpeg(
        graph=graph,
        validation_duration=1.0,
    )

    print(
        "ffmpeg_valid:",
        graph.metadata.get("ffmpeg_valid"),
    )
    print(
        "ffmpeg_returncode:",
        graph.metadata.get(
            "ffmpeg_returncode"
        ),
    )

    if graph.issues:
        print("\n=== Issues ===")

        for issue in graph.issues:
            print(issue.to_dict())

    output_path.write_text(
        json.dumps(
            graph.to_dict(),
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    assert graph.metadata["ffmpeg_valid"] is True
    assert len(graph.issues) == 0

    print(
        "\nDONE: FFmpeg FilterGraph builder "
        "test completed."
    )


if __name__ == "__main__":
    main()