from __future__ import annotations

from app.asset.providers import build_default_asset_provider_runtime
from app.asset.search.runtime import AssetSearchRuntime


def build_default_asset_search_runtime() -> AssetSearchRuntime:
    return AssetSearchRuntime(
        provider_runtime=build_default_asset_provider_runtime(),
    )