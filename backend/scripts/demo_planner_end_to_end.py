from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db.session import SessionLocal
from app.planner import (
    PlannerContext,
    PlannerRequest,
    PlannerSegment,
    build_planner_asset_orchestrator_integration,
)


def main() -> None:
    db = SessionLocal()

    try:
        integration = build_planner_asset_orchestrator_integration(db)

        request = PlannerRequest(
            context=PlannerContext(
                production_id="221e4b01-5fb9-4b4a-a549-4fb32c455059",
                platform="tiktok",
                editing_style="viral",
                story_type="problem_solution",
                language="vi",
                metadata={
                    "total_duration": 18,
                    "demo": "planner_end_to_end",
                },
            ),
            segments=[
                PlannerSegment(
                    segment_id="seg_001",
                    start_time=0,
                    end_time=4,
                    text="Sai lầm lớn nhất là bạn đang mất quá nhiều thời gian để edit video thủ công.",
                    segment_type="hook",
                    emotion="surprised",
                    importance_score=0.9,
                    viral_potential_score=0.95,
                ),
                PlannerSegment(
                    segment_id="seg_002",
                    start_time=4,
                    end_time=10,
                    text="AI có thể tự động hiểu nội dung và dựng video nhanh hơn.",
                    segment_type="solution",
                    emotion="excited",
                    importance_score=0.8,
                    viral_potential_score=0.75,
                ),
                PlannerSegment(
                    segment_id="seg_003",
                    start_time=10,
                    end_time=18,
                    text="Chỉ cần upload video, AI sẽ tự tìm b-roll, nhạc, hiệu ứng và dựng timeline.",
                    segment_type="cta",
                    emotion="inspirational",
                    importance_score=0.85,
                    viral_potential_score=0.8,
                ),
            ],
        )

        result = integration.run(request)
        payload = result.to_dict()

        output_dir = Path("storage/demo_outputs")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / "planner_end_to_end_result.json"
        output_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )

        print("=== Planner End-to-End Demo ===")
        print("production_id:", payload["production_id"])
        print("asset_plan_item_count:", payload["metadata"]["asset_plan_item_count"])
        print("asset_clip_count:", payload["metadata"]["asset_clip_count"])
        print("failed_asset_count:", payload["metadata"]["failed_asset_count"])
        print("output:", str(output_path))

        print("\n=== Asset Clips ===")
        for clip in payload["asset_result"]["asset_clips"]:
            print(
                {
                    "asset_type": clip["asset_type"],
                    "track_type": clip["track_type"],
                    "start_time": clip["start_time"],
                    "end_time": clip["end_time"],
                    "local_path": clip["local_path"],
                    "title": clip["title"],
                    "provider": clip["metadata"].get("provider_key"),
                }
            )

        print("\nDONE: Planner end-to-end demo completed.")

    finally:
        db.close()


if __name__ == "__main__":
    main()