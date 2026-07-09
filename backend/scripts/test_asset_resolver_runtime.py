from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.asset.resolver import AssetResolveRequest, build_asset_resolver_runtime
from app.db.session import SessionLocal


def main() -> None:
    db = SessionLocal()

    try:
        resolver = build_asset_resolver_runtime(db)

        print("=== First Resolve ===")
        first = resolver.resolve(
            AssetResolveRequest(
                query="person editing video on laptop",
                asset_type="broll",
                preferred_orientation="portrait",
                preferred_duration=6,
                commercial_use=True,
                per_page=5,
            )
        )
        print(first)

        print("\n=== Second Resolve / Cache Test ===")
        second = resolver.resolve(
            AssetResolveRequest(
                query="person editing video on laptop",
                asset_type="broll",
                preferred_orientation="portrait",
                preferred_duration=6,
                commercial_use=True,
                per_page=5,
            )
        )
        print(second)

        print("\nDONE: Asset resolver runtime test completed.")

    finally:
        db.close()


if __name__ == "__main__":
    main()