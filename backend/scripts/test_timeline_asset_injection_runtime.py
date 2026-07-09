from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db.session import SessionLocal
from app.timeline.asset_injector import (
    TimelineAssetInjectionRequest,
    TimelineAssetInstruction,
    build_timeline_asset_injection_runtime,
)


def main() -> None:
    db = SessionLocal()

    try:
        runtime = build_timeline_asset_injection_runtime(db)

        result = runtime.inject(
            TimelineAssetInjectionRequest(
                production_id="221e4b01-5fb9-4b4a-a549-4fb32c455059",
                instructions=[
                    TimelineAssetInstruction(
                        query="person editing video on laptop",
                        asset_type="broll",
                        track_type="broll",
                        start_time=4.5,
                        end_time=9.5,
                        preferred_orientation="portrait",
                        layer=2,
                        opacity=1.0,
                        metadata={"reason": "support manual editing pain point"},
                    ),
                    TimelineAssetInstruction(
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
            )
        )

        print("=== Timeline Asset Injection Result ===")
        print(result.to_dict())

        print("\nDONE: Timeline asset injection runtime test completed.")

    finally:
        db.close()


if __name__ == "__main__":
    main()