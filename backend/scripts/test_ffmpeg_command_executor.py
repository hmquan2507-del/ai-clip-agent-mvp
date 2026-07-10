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
    build_ffmpeg_command_builder,
    build_ffmpeg_command_executor,
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
                "storage/ffmpeg_executor_test"
            ),
        )
    )

    preload_result = (
        build_render_asset_preloader()
        .preload(context)
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

    assert (
        instruction_plan.metadata["valid"]
        is True
    )

    graph = (
        build_ffmpeg_filtergraph_builder()
        .build(instruction_plan)
    )

    graph = (
        build_ffmpeg_filtergraph_validator()
        .validate_with_ffmpeg(
            graph=graph,
            validation_duration=1.0,
        )
    )

    assert (
        graph.metadata["ffmpeg_valid"]
        is True
    )

    command = (
        build_ffmpeg_command_builder()
        .build(
            graph=graph,
            enable_progress=True,
            log_level="error",
        )
    )

    progress_values: list[float] = []

    def on_progress(event) -> None:
        progress_values.append(
            event.progress
        )

        print(
            "progress:",
            event.progress,
            "out_time:",
            event.out_time_seconds,
            "speed:",
            event.speed,
        )

    executor = (
        build_ffmpeg_command_executor()
    )

    result = executor.execute(
        production_id=execution.production_id,
        command=command,
        progress_callback=on_progress,
    )

    report_path = executor.write_report(
        result=result,
        report_path=(
            "storage/demo_outputs/"
            "ffmpeg_execution_report.json"
        ),
    )

    command_path = Path(
        "storage/demo_outputs/"
        "ffmpeg_command.json"
    )

    command_path.write_text(
        json.dumps(
            command.to_dict(),
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    print("\n=== FFmpeg Execution ===")
    print("success:", result.success)
    print("returncode:", result.returncode)
    print("output_path:", result.output_path)
    print(
        "output_file_size:",
        result.output_file_size,
    )
    print(
        "output_duration:",
        result.output_duration,
    )
    print(
        "output_resolution:",
        result.output_width,
        "x",
        result.output_height,
    )
    print(
        "output_fps:",
        result.output_fps,
    )
    print(
        "video_codec:",
        result.output_video_codec,
    )
    print(
        "audio_codec:",
        result.output_audio_codec,
    )
    print(
        "progress_event_count:",
        len(result.progress_events),
    )
    print(
        "issue_count:",
        len(result.issues),
    )
    print("report:", report_path)

    if result.issues:
        print("\n=== Issues ===")

        for issue in result.issues:
            print(issue.to_dict())

    if result.stderr_tail:
        print("\n=== FFmpeg stderr tail ===")
        print(result.stderr_tail)

    assert result.success is True
    assert result.returncode == 0
    assert len(result.issues) == 0

    output_path = Path(
        result.output_path
    )

    assert output_path.exists()
    assert output_path.is_file()
    assert output_path.stat().st_size > 0

    assert result.output_duration is not None
    assert result.output_duration > 0

    assert result.output_width == 1080
    assert result.output_height == 1920

    assert result.output_video_codec
    assert result.output_audio_codec

    assert progress_values
    assert progress_values[-1] == 100.0

    print(
        "\nDONE: FFmpeg command executor "
        "test completed."
    )


if __name__ == "__main__":
    main()