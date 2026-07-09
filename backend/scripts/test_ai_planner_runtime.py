from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.planner import (
    PlannerContext,
    PlannerRequest,
    PlannerSegment,
    build_ai_planner_runtime,
)


def main() -> None:
    runtime = build_ai_planner_runtime()

    request = PlannerRequest(
        context=PlannerContext(
            production_id="221e4b01-5fb9-4b4a-a549-4fb32c455059",
            platform="tiktok",
            editing_style="viral",
            story_type="problem_solution",
            language="vi",
            metadata={"total_duration": 18},
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
        ],
    )

    plan = runtime.build_plan(request)

    print("=== AI Asset Planner Result ===")
    print(plan.to_dict())

    print("\nDONE: AI planner runtime test completed.")


if __name__ == "__main__":
    main()