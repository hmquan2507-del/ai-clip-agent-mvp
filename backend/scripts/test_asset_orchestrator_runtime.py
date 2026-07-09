from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.asset.orchestrator import (
    AssetOrchestrationRequest,
    AssetPlanItem,
    build_asset_orchestrator_runtime,
)
from app.db.session import SessionLocal


def main() -> None:
    db = SessionLocal()

    try:
        runtime = build_asset_orchestrator_runtime(db)

        result = runtime.run(
            AssetOrchestrationRequest(
                production_id="221e4b01-5fb9-4b4a-a549-4fb32c455059",
                plan_items=[
                    AssetPlanItem(
                        query="person editing video on laptop",
                        asset_type="broll",
                        track_type="broll",
                        start_time=4.5,
                        end_time=9.5,
                        preferred_orientation="portrait",
                        layer=2,
                        opacity=1.0,
                        metadata={"reason": "manual editing pain point"},
                    ),
                    AssetPlanItem(
                        query="office worker using computer",
                        asset_type="broll",
                        track_type="broll",
                        start_time=10.0,
                        end_time=14.0,
                        preferred_orientation="portrait",
                        layer=2,
                        opacity=1.0,
                        metadata={"reason": "AI editing workflow explanation"},
                    ),
                    AssetPlanItem(
                        query="whoosh transition",
                        asset_type="sound_effect",
                        track_type="sfx",
                        start_time=9.5,
                        end_time=10.2,
                        preferred_duration=1.0,
                        layer=3,
                        volume=0.8,
                        metadata={"reason": "transition emphasis"},
                    ),
                ],
                metadata={
                    "source": "test_asset_orchestrator_runtime",
                    "mode": "demo",
                },
            )
        )

        print("=== Asset Orchestration Result ===")
        print(result.to_dict())

        print("\nDONE: Asset orchestrator runtime test completed.")

    finally:
        db.close()


if __name__ == "__main__":
    main()