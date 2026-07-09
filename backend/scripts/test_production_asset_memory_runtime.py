from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.asset.memory import (
    AssetMemoryLookupRequest,
    build_production_asset_memory_runtime,
)
from app.db.session import SessionLocal
from app.timeline.asset_injector import (
    TimelineAssetInjectionRequest,
    TimelineAssetInstruction,
    build_timeline_asset_injection_runtime,
)


def main() -> None:
    production_id = "221e4b01-5fb9-4b4a-a549-4fb32c455059"

    db = SessionLocal()

    try:
        memory = build_production_asset_memory_runtime()
        runtime = build_timeline_asset_injection_runtime(db)

        first = runtime.inject(
            TimelineAssetInjectionRequest(
                production_id=production_id,
                instructions=[
                    TimelineAssetInstruction(
                        query="person editing video on laptop",
                        asset_type="broll",
                        track_type="broll",
                        start_time=0,
                        end_time=4,
                        preferred_orientation="portrait",
                        layer=2,
                        opacity=1.0,
                    )
                ],
            )
        )

        second = runtime.inject(
            TimelineAssetInjectionRequest(
                production_id=production_id,
                instructions=[
                    TimelineAssetInstruction(
                        query="person editing video on laptop",
                        asset_type="broll",
                        track_type="broll",
                        start_time=4,
                        end_time=8,
                        preferred_orientation="portrait",
                        layer=2,
                        opacity=1.0,
                    )
                ],
            )
        )

        lookup = memory.lookup(
            AssetMemoryLookupRequest(
                production_id=production_id,
                asset_type="broll",
            )
        )

        print("=== First ===")
        print(first.to_dict())

        print("\n=== Second ===")
        print(second.to_dict())

        print("\n=== Memory ===")
        for usage in lookup.usages:
            print(usage)

        print("\nused_count:", len(lookup.usages))
        print("DONE: Production asset memory runtime test completed.")

    finally:
        db.close()


if __name__ == "__main__":
    main()