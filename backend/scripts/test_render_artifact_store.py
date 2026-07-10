from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from app.render.execution import (
    build_render_architecture_runtime,
    build_render_artifact_store,
)
from app.render.ffmpeg.execution.models import (
    FFmpegCommand,
    FFmpegExecutionResult,
)
from scripts.test_render_architecture_runtime import (
    load_execution_timeline,
)


def main() -> None:
    execution_path = Path(
        "storage/demo_outputs/"
        "execution_timeline.json"
    )

    report_path = Path(
        "storage/demo_outputs/"
        "ffmpeg_execution_report.json"
    )

    if not execution_path.exists():
        raise RuntimeError(
            "Run test_timeline_compiler_runtime.py first."
        )

    if not report_path.exists():
        raise RuntimeError(
            "Run test_ffmpeg_command_executor.py first."
        )

    execution = load_execution_timeline(
        execution_path
    )

    payload = json.loads(
        report_path.read_text(
            encoding="utf-8"
        )
    )

    context = (
        build_render_architecture_runtime()
        .build_context(
            execution_timeline=execution,
            storage_root=(
                "storage/render_artifact_test"
            ),
        )
    )

    command_payload = payload["command"]

    command = FFmpegCommand(
        binary=command_payload["binary"],
        arguments=command_payload["arguments"],
        output_path=command_payload[
            "output_path"
        ],
        duration=command_payload["duration"],
        metadata=command_payload.get(
            "metadata"
        ) or {},
    )

    execution_result = FFmpegExecutionResult(
        production_id=payload["production_id"],
        success=payload["success"],
        returncode=payload["returncode"],
        output_path=payload["output_path"],
        command=command,
        started_at=payload["started_at"],
        finished_at=payload["finished_at"],
        duration_seconds=payload[
            "duration_seconds"
        ],
        progress_events=[],
        issues=[],
        stderr_tail=payload.get(
            "stderr_tail"
        ),
        output_file_size=payload.get(
            "output_file_size"
        ),
        output_duration=payload.get(
            "output_duration"
        ),
        output_width=payload.get(
            "output_width"
        ),
        output_height=payload.get(
            "output_height"
        ),
        output_fps=payload.get(
            "output_fps"
        ),
        output_video_codec=payload.get(
            "output_video_codec"
        ),
        output_audio_codec=payload.get(
            "output_audio_codec"
        ),
        metadata=payload.get(
            "metadata"
        ) or {},
    )

    result = build_render_artifact_store().store(
        context=context,
        execution_result=execution_result,
        generate_thumbnail=True,
        generate_report=True,
    )

    output_path = Path(
        "storage/demo_outputs/"
        "render_artifact_store_result.json"
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

    print("=== Render Artifact Store ===")
    print("success:", result.success)
    print(
        "artifact_count:",
        len(result.artifacts),
    )
    print(
        "artifact_types:",
        [
            item.artifact_type
            for item in result.artifacts
        ],
    )
    print(
        "issue_count:",
        len(result.issues),
    )
    print(
        "manifest_path:",
        result.manifest_path,
    )
    print(
        "context_artifact_count:",
        len(context.artifacts),
    )
    print("output:", output_path)

    assert result.success is True
    assert len(result.issues) == 0
    assert len(result.artifacts) >= 3

    artifact_types = {
        item.artifact_type
        for item in result.artifacts
    }

    assert "final_video" in artifact_types
    assert "thumbnail" in artifact_types
    assert "render_report" in artifact_types

    for artifact in result.artifacts:
        path = Path(artifact.local_path)

        assert path.exists()
        assert path.is_file()
        assert path.stat().st_size > 0
        assert artifact.checksum

    assert len(context.artifacts) == len(
        result.artifacts
    )

    print(
        "\nDONE: Render artifact store test "
        "completed."
    )


if __name__ == "__main__":
    main()