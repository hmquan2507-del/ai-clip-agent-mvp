from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.timeline.semantic import (
    TimelineSemanticEnrichmentEngine,
    build_timeline_semantic_engine,
)


def main() -> None:
    input_path = Path("storage/demo_outputs/planner_end_to_end_result.json")

    if not input_path.exists():
        raise RuntimeError(
            "Missing planner output. Run scripts/demo_planner_end_to_end.py first."
        )

    payload = json.loads(input_path.read_text(encoding="utf-8"))

    planner_request = {
        "segments": [
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
    }

    semantic_engine = build_timeline_semantic_engine()
    analysis = semantic_engine.analyze(
        production_id=payload["production_id"],
        planner_payload=payload,
        asset_result=payload,
    )

    enriched = TimelineSemanticEnrichmentEngine().enrich(
        analysis=analysis,
        planner_request=planner_request,
    )

    print("=== Timeline Semantic Enrichment ===")
    print(enriched.to_dict())

    print("\nDONE: Timeline semantic enrichment test completed.")


if __name__ == "__main__":
    main()