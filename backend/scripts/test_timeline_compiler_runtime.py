from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)
from app.timeline.compiler import (
    TimelineSourceMedia,
    build_timeline_compiler_runtime,
)
from app.timeline.finalizer.models import (
    FinalTimeline,
    FinalTimelineClip,
    FinalTimelineEffect,
    FinalTimelineTrack,
    FinalTimelineTransition,
)


def load_final_timeline(path: Path) -> FinalTimeline:
    payload = json.loads(
        path.read_text(encoding="utf-8")
    )

    tracks = []

    for track_payload in payload["tracks"]:
        clips = [
            FinalTimelineClip(
                clip_id=item["clip_id"],
                track_type=item["track_type"],
                start_time=item["start_time"],
                end_time=item["end_time"],
                layer=item["layer"],
                asset_id=item.get("asset_id"),
                local_path=item.get("local_path"),
                content=item.get("content"),
                volume=item.get("volume"),
                opacity=item.get("opacity"),
                speed=item.get("speed"),
                metadata=item.get("metadata") or {},
            )
            for item in track_payload["clips"]
        ]

        tracks.append(
            FinalTimelineTrack(
                track_id=track_payload["track_id"],
                track_type=track_payload["track_type"],
                layer=track_payload["layer"],
                clips=clips,
                metadata=(
                    track_payload.get("metadata") or {}
                ),
            )
        )

    effects = [
        FinalTimelineEffect(
            effect_id=item["effect_id"],
            target_id=item["target_id"],
            effect_type=item["effect_type"],
            start_time=item["start_time"],
            end_time=item["end_time"],
            parameters=item.get("parameters") or {},
            metadata=item.get("metadata") or {},
        )
        for item in payload["effects"]
    ]

    transitions = [
        FinalTimelineTransition(
            transition_id=item["transition_id"],
            target_id=item["target_id"],
            transition_type=item["transition_type"],
            at_time=item["at_time"],
            duration=item["duration"],
            parameters=item.get("parameters") or {},
            metadata=item.get("metadata") or {},
        )
        for item in payload["transitions"]
    ]

    canvas = payload["canvas"]

    return FinalTimeline(
        production_id=payload["production_id"],
        version=payload["version"],
        duration=payload["duration"],
        width=canvas["width"],
        height=canvas["height"],
        fps=canvas["fps"],
        tracks=tracks,
        effects=effects,
        transitions=transitions,
        metadata=payload.get("metadata") or {},
    )


def main() -> None:
    input_path = Path(
        "storage/demo_outputs/final_timeline.json"
    )

    if not input_path.exists():
        raise RuntimeError(
            "Run test_timeline_finalizer_runtime.py first."
        )

    timeline = load_final_timeline(input_path)

    compiler = build_timeline_compiler_runtime()

    execution = compiler.compile(
    timeline=timeline,
    source_media=TimelineSourceMedia(
        asset_id="demo_source_asset",
        local_path="storage/uploads/demo_source_video.mp4",
        metadata={
            "source": "timeline_compiler_test",
        },
    ),
)

    output_path = Path(
        "storage/demo_outputs/execution_timeline.json"
    )

    output_path.write_text(
        json.dumps(
            execution.to_dict(),
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    result = execution.to_dict()

    print("=== Execution Timeline ===")
    print("production_id:", result["production_id"])
    print("version:", result["version"])
    print("duration:", result["duration"])
    print("input_count:", len(result["inputs"]))
    print(
        "instruction_count:",
        len(result["instructions"]),
    )
    print("issue_count:", len(result["issues"]))
    print(
        "render_ready:",
        result["metadata"]["render_ready"],
    )
    print("output:", output_path)

    if result["issues"]:
        print("\n=== Compiler Issues ===")
        for issue in result["issues"]:
            print(issue)

    print(
        "\nDONE: Timeline compiler runtime test completed."
    )


if __name__ == "__main__":
    main()