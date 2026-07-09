from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.asset.ranking import (
    AssetRankingRequest,
    build_default_asset_ranking_runtime,
)
from app.asset.search import AssetSearchRequest, build_default_asset_search_runtime


def main() -> None:
    search_runtime = build_default_asset_search_runtime()
    ranking_runtime = build_default_asset_ranking_runtime()

    print("=== Search B-roll Candidates ===")
    search = search_runtime.search(
        AssetSearchRequest(
            query="person editing video on laptop",
            asset_type="broll",
            per_page=5,
            orientation="portrait",
        )
    )
    print("candidates:", len(search.results))

    ranking = ranking_runtime.rank(
        AssetRankingRequest(
            query=search.query,
            asset_type=search.asset_type,
            candidates=search.results,
            preferred_orientation="portrait",
            preferred_duration=6,
            commercial_use=True,
            limit=5,
        )
    )

    print("\n=== Ranked B-roll Assets ===")
    print("metadata:", ranking.metadata)

    for item in ranking.ranked_assets:
        print(
            {
                "provider": item.asset.provider_key,
                "id": item.asset.provider_asset_id,
                "score": item.score,
                "title": item.asset.title,
                "license": item.asset.license,
                "reasons": item.reasons,
                "penalties": item.penalties,
            }
        )

    print("\n=== Search SFX Candidates ===")
    sfx_search = search_runtime.search(
        AssetSearchRequest(
            query="whoosh transition",
            asset_type="sound_effect",
            per_page=5,
        )
    )
    print("candidates:", len(sfx_search.results))

    sfx_ranking = ranking_runtime.rank(
        AssetRankingRequest(
            query=sfx_search.query,
            asset_type=sfx_search.asset_type,
            candidates=sfx_search.results,
            preferred_duration=2,
            commercial_use=True,
            limit=5,
        )
    )

    print("\n=== Ranked SFX Assets ===")
    print("metadata:", sfx_ranking.metadata)

    for item in sfx_ranking.ranked_assets:
        print(
            {
                "provider": item.asset.provider_key,
                "id": item.asset.provider_asset_id,
                "score": item.score,
                "title": item.asset.title,
                "license": item.asset.license,
                "reasons": item.reasons,
                "penalties": item.penalties,
            }
        )

    print("\n=== Rejected SFX Assets ===")
    for item in sfx_ranking.rejected_assets[:5]:
        print(
            {
                "provider": item.asset.provider_key,
                "id": item.asset.provider_asset_id,
                "score": item.score,
                "title": item.asset.title,
                "license": item.asset.license,
                "penalties": item.penalties,
            }
        )


if __name__ == "__main__":
    main()