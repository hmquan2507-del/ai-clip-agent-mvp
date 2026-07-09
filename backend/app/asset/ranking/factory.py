from __future__ import annotations

from app.asset.ranking.runtime import AssetRankingRuntime


def build_default_asset_ranking_runtime() -> AssetRankingRuntime:
    return AssetRankingRuntime()