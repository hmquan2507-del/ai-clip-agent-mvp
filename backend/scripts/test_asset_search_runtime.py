from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.asset.search import AssetSearchRequest, build_default_asset_search_runtime


def main() -> None:
    runtime = build_default_asset_search_runtime()

    print("=== B-roll Search Runtime ===")
    broll = runtime.search(
        AssetSearchRequest(
            query="person editing video on laptop",
            asset_type="broll",
            per_page=3,
            orientation="portrait",
        )
    )
    print("providers:", broll.provider_count)
    print("results:", len(broll.results))
    print("metadata:", broll.metadata)
    print("first:", broll.results[:1])

    print("\n=== SFX Search Runtime ===")
    sfx = runtime.search(
        AssetSearchRequest(
            query="whoosh transition",
            asset_type="sound_effect",
            per_page=3,
        )
    )
    print("providers:", sfx.provider_count)
    print("results:", len(sfx.results))
    print("metadata:", sfx.metadata)
    print("first:", sfx.results[:1])


if __name__ == "__main__":
    main()