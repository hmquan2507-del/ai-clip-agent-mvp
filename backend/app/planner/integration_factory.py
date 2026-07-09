from __future__ import annotations

from sqlalchemy.orm import Session

from app.planner.orchestrator_integration import PlannerAssetOrchestratorIntegration


def build_planner_asset_orchestrator_integration(
    db: Session,
) -> PlannerAssetOrchestratorIntegration:
    return PlannerAssetOrchestratorIntegration(db=db)