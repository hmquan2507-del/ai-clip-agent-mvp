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

        result = resolver.resolve(
            AssetResolveRequest(
                query="corporate background music",
                asset_type="music",
                preferred_duration=20,
                commercial_use=True,
                provider_keys=["internal_music"],
            )
        )

        print("=== Music Resolve Result ===")
        print(result)

        print("\nDONE: Attribution + internal music test completed.")

    finally:
        db.close()


if __name__ == "__main__":
    main()