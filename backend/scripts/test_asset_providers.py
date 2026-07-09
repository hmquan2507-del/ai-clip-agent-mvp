from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.asset.providers import (
    AssetProviderSearchRequest,
    build_default_asset_provider_runtime,
)


def main() -> None:
    runtime = build_default_asset_provider_runtime()

    print("=== Provider Health ===")
    for item in runtime.health_all():
        print(item)

    print("\n=== Pexels B-roll Search ===")
    try:
        result = runtime.search(
            "pexels",
            AssetProviderSearchRequest(
                query="person editing video on laptop",
                asset_type="broll",
                per_page=5,
                orientation="portrait",
            ),
        )
        print("results:", len(result.results))
        print(result.results[:1])
    except Exception as error:
        print("Pexels search failed:", error)

    print("\n=== Pixabay Video Search ===")
    try:
        result = runtime.search(
            "pixabay",
            AssetProviderSearchRequest(
                query="video editing laptop",
                asset_type="broll",
                per_page=5,
            ),
        )
        print("results:", len(result.results))
        print(result.results[:1])
    except Exception as error:
        print("Pixabay search failed:", error)

    print("\n=== Freesound SFX Search ===")
    try:
        result = runtime.search(
            "freesound",
            AssetProviderSearchRequest(
                query="whoosh transition",
                asset_type="sound_effect",
                per_page=5,
            ),
        )
        print("results:", len(result.results))
        print(result.results[:1])
    except Exception as error:
        print("Freesound search failed:", error)


if __name__ == "__main__":
    main()