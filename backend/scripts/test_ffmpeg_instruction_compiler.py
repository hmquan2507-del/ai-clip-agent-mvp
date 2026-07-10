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
                "storage/ffmpeg_instruction_test"
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
            "Asset preload failed before "
            "FFmpeg instruction compilation."
        )

    compiler = (
        build_ffmpeg_instruction_compiler()
    )

    validator = (
        build_ffmpeg_instruction_plan_validator()
    )

    plan = compiler.compile(
        context=context,
        preload_result=preload_result,
    )

    plan = validator.validate(plan)

    output_path = Path(
        "storage/demo_outputs/"
        "ffmpeg_instruction_plan.json"
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

    instruction_types = [
        (
            item.instruction_type.value
            if hasattr(
                item.instruction_type,
                "value",
            )
            else str(item.instruction_type)
        )
        for item in plan.instructions
    ]

    print("=== FFmpeg Instruction Plan ===")
    print("production_id:", plan.production_id)
    print("version:", plan.version)
    print("input_count:", len(plan.inputs))
    print(
        "instruction_count:",
        len(plan.instructions),
    )
    print("issue_count:", len(plan.issues))
    print(
        "plan_valid:",
        plan.metadata["valid"],
    )
    print(
        "instruction_types:",
        sorted(set(instruction_types)),
    )
    print("output:", output_path)

    assert plan.metadata["valid"] is True
    assert len(plan.issues) == 0
    assert len(plan.inputs) == len(
        execution.inputs
    )
    assert len(plan.instructions) > 0

    assert "trim_video" in instruction_types
    assert "scale" in instruction_types
    assert "overlay" in instruction_types
    assert "trim_audio" in instruction_types
    assert "volume" in instruction_types
    assert "audio_delay" in instruction_types
    assert "draw_subtitle" in instruction_types
    assert "apply_video_effect" in (
        instruction_types
    )
    assert "apply_transition" in (
        instruction_types
    )
    assert instruction_types.count(
        "encode"
    ) == 1

    print(
        "\nDONE: FFmpeg instruction compiler "
        "test completed."
    )


if __name__ == "__main__":
    main()