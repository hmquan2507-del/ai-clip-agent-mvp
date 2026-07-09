from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.asset.cache import AssetCacheLookupRequest, build_asset_cache_runtime
from app.asset.runtime import AssetRuntime
from app.db.session import SessionLocal


def main() -> None:
    db = SessionLocal()

    try:
        cache_runtime = build_asset_cache_runtime(db)
        asset_runtime = AssetRuntime(db)

        assets = asset_runtime.repository.list_assets(asset_type="broll", limit=1)

        if not assets:
            raise RuntimeError(
                "No broll asset found. Run scripts/test_asset_download_runtime.py first."
            )

        asset = assets[0]

        print("=== Provider Asset Cache Lookup ===")
        result = cache_runtime.lookup(
            AssetCacheLookupRequest(
                query="person editing video on laptop",
                asset_type="broll",
                provider_key=asset.provider_key,
                provider_asset_id=asset.provider_asset_id,
            )
        )
        print(result)

        print("\n=== Keyword Cache Lookup ===")
        keyword_result = cache_runtime.lookup(
            AssetCacheLookupRequest(
                query="laptop editing creator",
                asset_type="broll",
            )
        )
        print(keyword_result)

        print("\n=== Cache Miss Lookup ===")
        miss = cache_runtime.lookup(
            AssetCacheLookupRequest(
                query="underwater volcano dragon",
                asset_type="broll",
            )
        )
        print(miss)

        print("\nDONE: Asset cache runtime test completed.")

    finally:
        db.close()


if __name__ == "__main__":
    main()