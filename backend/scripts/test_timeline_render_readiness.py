from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.timeline.compiler import (
    TimelineReadinessValidator,
    TimelineSourceMedia,
    build_timeline_compiler_runtime,
)
from scripts.test_timeline_compiler_runtime import load_final_timeline


def main() -> None:
    timeline_path = Path(
        "storage/demo_outputs/final_timeline.json"
    )

    if not timeline_path.exists():
        raise RuntimeError(
            "Run test_timeline_finalizer_runtime.py first."
        )

    timeline = load_final_timeline(timeline_path)

    source_media = TimelineSourceMedia(
        asset_id="demo_source_asset",
        local_path="storage/uploads/demo_source_video.mp4",
        metadata={
            "source": "14.13_hardening_test",
        },
    )

    execution = build_timeline_compiler_runtime().compile(
        timeline=timeline,
        source_media=source_media,
    )

    readiness = TimelineReadinessValidator().validate(
        execution
    )

    print("=== Timeline Readiness ===")
    print(readiness.to_dict())

    assert readiness.compile_ready is True
    assert readiness.assets_resolved is True
    assert readiness.media_validated is True
    assert readiness.render_ready is True

    print(
        "\nDONE: Timeline render readiness test completed."
    )


if __name__ == "__main__":
    main()