from __future__ import annotations

from sqlalchemy.orm import Session

from app.asset.orchestrator.runtime import AssetOrchestratorRuntime


def build_asset_orchestrator_runtime(
    db: Session,
) -> AssetOrchestratorRuntime:
    return AssetOrchestratorRuntime(db=db)