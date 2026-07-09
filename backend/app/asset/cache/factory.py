from __future__ import annotations

from sqlalchemy.orm import Session

from app.asset.cache.runtime import AssetCacheRuntime


def build_asset_cache_runtime(db: Session) -> AssetCacheRuntime:
    return AssetCacheRuntime(db=db)