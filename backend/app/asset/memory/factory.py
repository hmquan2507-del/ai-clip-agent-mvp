from __future__ import annotations

from app.asset.memory.runtime import ProductionAssetMemoryRuntime


_GLOBAL_ASSET_MEMORY = ProductionAssetMemoryRuntime()


def build_production_asset_memory_runtime() -> ProductionAssetMemoryRuntime:
    return _GLOBAL_ASSET_MEMORY