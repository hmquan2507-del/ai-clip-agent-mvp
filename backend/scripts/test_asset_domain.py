from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.asset.enums import AssetStatus, AssetType, ProviderKey
from app.asset.models import AssetDomain, AssetReference
from app.asset.runtime import AssetRuntime
from app.db.session import SessionLocal


def main() -> None:
    db = SessionLocal()

    try:
        runtime = AssetRuntime(db)

        row = runtime.save_asset(
            AssetDomain(
                provider_key=ProviderKey.INTERNAL,
                provider_asset_id="demo_asset_001",
                asset_type=AssetType.BROLL,
                status=AssetStatus.READY,
                title="Demo laptop editing b-roll",
                description="Demo internal b-roll asset.",
                tags=["laptop", "editing", "creator"],
                keywords=["video editing", "laptop", "creator"],
                metadata={
                    "orientation": "9:16",
                    "scene": "workspace",
                    "emotion": "focused",
                },
                local_path="storage/assets/demo/laptop-editing.mp4",
                duration=5.0,
                width=1080,
                height=1920,
                fps=30,
                license="internal",
                language="vi",
            )
        )

        payload = runtime.load_asset_payload(row.id)

        reference = AssetReference(
            asset_id=row.id,
            track_type="broll",
            start_time=4.5,
            end_time=9.5,
            layer=2,
            opacity=1.0,
            transform={"fit": "cover", "motion": "zoom_in"},
        )

        print("Asset saved:")
        print(payload)

        print("\nAsset reference:")
        print(reference.to_dict())

        print("\nDONE: Asset domain test completed.")

    finally:
        db.close()


if __name__ == "__main__":
    main()