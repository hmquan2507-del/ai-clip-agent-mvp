from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.timeline.semantic import build_timeline_semantic_engine


def main() -> None:
    input_path = Path("storage/demo_outputs/planner_end_to_end_result.json")

    if not input_path.exists():
        raise RuntimeError(
            "Missing planner output. Run scripts/demo_planner_end_to_end.py first."
        )

    payload = json.loads(input_path.read_text(encoding="utf-8"))

    engine = build_timeline_semantic_engine()

    analysis = engine.analyze(
        production_id=payload["production_id"],
        planner_payload=payload,
        asset_result=payload,
    )

    print("=== Timeline Semantic Analysis ===")
    print(analysis.to_dict())

    print("\nDONE: Timeline semantic engine test completed.")


if __name__ == "__main__":
    main()