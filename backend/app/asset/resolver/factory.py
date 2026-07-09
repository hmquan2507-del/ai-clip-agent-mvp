from __future__ import annotations

from sqlalchemy.orm import Session

from app.asset.resolver.runtime import AssetResolverRuntime


def build_asset_resolver_runtime(db: Session) -> AssetResolverRuntime:
    return AssetResolverRuntime(db=db)