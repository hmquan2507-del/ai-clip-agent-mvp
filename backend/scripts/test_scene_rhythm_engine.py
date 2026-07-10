from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.audio.beat_detection import (
    BeatDetectionRequest,
    build_beat_detection_runtime,
)
from app.subtitle.timing import (
    SubtitleTimingSegment,
    build_subtitle_timing_optimizer,
)
from app.timeline.broll_placement import build_smart_broll_placement_runtime
from app.timeline.motion_planning import build_motion_planning_runtime
from app.timeline.scene_rhythm import build_scene_rhythm_engine
from app.timeline.semantic import (
    TimelineSemanticEnrichmentEngine,
    build_timeline_semantic_engine,
)
from app.timeline.shot_selection import build_shot_selection_runtime
from app.timeline.transition_planning import build_transition_planning_runtime


def main() -> None:
    input_path = Path("storage/demo_outputs/planner_end_to_end_result.json")

    if not input_path.exists():
        raise RuntimeError(
            "Missing planner output. Run scripts/demo_planner_end_to_end.py first."
        )

    payload = json.loads(input_path.read_text(encoding="utf-8"))

    segment_payloads = [
        {
            "segment_id": "seg_001",
            "start_time": 0,
            "end_time": 4,
            "text": "Sai lầm lớn nhất là bạn đang mất quá nhiều thời gian để edit video thủ công.",
            "segment_type": "hook",
            "emotion": "surprised",
            "importance_score": 0.9,
            "viral_potential_score": 0.95,
        },
        {
            "segment_id": "seg_002",
            "start_time": 4,
            "end_time": 10,
            "text": "AI có thể tự động hiểu nội dung và dựng video nhanh hơn.",
            "segment_type": "solution",
            "emotion": "excited",
            "importance_score": 0.8,
            "viral_potential_score": 0.75,
        },
        {
            "segment_id": "seg_003",
            "start_time": 10,
            "end_time": 18,
            "text": "Chỉ cần upload video, AI sẽ tự tìm b-roll, nhạc, hiệu ứng và dựng timeline.",
            "segment_type": "cta",
            "emotion": "inspirational",
            "importance_score": 0.85,
            "viral_potential_score": 0.8,
        },
    ]

    semantic = build_timeline_semantic_engine().analyze(
        production_id=payload["production_id"],
        planner_payload=payload,
        asset_result=payload,
    )

    enriched = TimelineSemanticEnrichmentEngine().enrich(
        analysis=semantic,
        planner_request={"segments": segment_payloads},
    )

    shots = build_shot_selection_runtime().select(enriched)

    placements = build_smart_broll_placement_runtime().place(
        analysis=enriched,
        shot_result=shots,
    )

    motions = build_motion_planning_runtime().plan(
        production_id=payload["production_id"],
        placements=placements,
    )

    transitions = build_transition_planning_runtime().plan(
        production_id=payload["production_id"],
        placements=placements,
    )

    subtitles = build_subtitle_timing_optimizer().optimize(
        production_id=payload["production_id"],
        segments=[
            SubtitleTimingSegment(
                segment_id=item["segment_id"],
                start_time=item["start_time"],
                end_time=item["end_time"],
                text=item["text"],
                segment_type=item["segment_type"],
                importance_score=item["importance_score"],
            )
            for item in segment_payloads
        ],
    )

    music_path = next(
        (
            asset.local_path
            for asset in enriched.assets
            if asset.asset_type == "music" and asset.local_path
        ),
        None,
    )

    if music_path is None:
        raise RuntimeError("No music asset found for beat detection.")

    beats = build_beat_detection_runtime().detect(
        BeatDetectionRequest(
            audio_path=music_path,
            start_time=0.0,
            end_time=18.0,
            expected_bpm=120.0,
            metadata={
                "production_id": payload["production_id"],
            },
        )
    )

    rhythm = build_scene_rhythm_engine().build(
        analysis=enriched,
        subtitle_result=subtitles,
        beat_result=beats,
        shot_result=shots,
        motion_result=motions,
        transition_result=transitions,
    )

    print("=== Scene Rhythm Result ===")
    print(rhythm.to_dict())

    print("\nDONE: Scene rhythm engine test completed.")


if __name__ == "__main__":
    main()