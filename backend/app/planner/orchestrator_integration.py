from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.orm import Session

from app.asset.orchestrator import (
    AssetOrchestrationRequest,
    AssetOrchestrationResult,
    AssetOrchestratorRuntime,
)
from app.planner.conflict_resolver import PlannerConflictResolver
from app.planner.execution_graph import PlannerExecutionGraphBuilder
from app.planner.export_contract import PlannerExportContract
from app.planner.models import PlannerRequest
from app.planner.runtime import AIPlannerRuntime
from app.planner.validator import PlannerValidator
from app.planner.diversity_guard import PlannerDiversityGuard
from app.planner.optimizer import PlannerOptimizer

@dataclass
class PlannerAssetExecutionResult:
    production_id: str
    planner_payload: dict[str, Any]
    asset_result: AssetOrchestrationResult
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": self.production_id,
            "planner_payload": self.planner_payload,
            "asset_result": self.asset_result.to_dict(),
            "metadata": self.metadata,
        }


class PlannerAssetOrchestratorIntegration:
    def __init__(
        self,
        db: Session,
        planner_runtime: AIPlannerRuntime | None = None,
        validator: PlannerValidator | None = None,
        conflict_resolver: PlannerConflictResolver | None = None,
        graph_builder: PlannerExecutionGraphBuilder | None = None,
        export_contract: PlannerExportContract | None = None,
        asset_orchestrator: AssetOrchestratorRuntime | None = None,
        diversity_guard: PlannerDiversityGuard | None = None,
        optimizer: PlannerOptimizer | None = None,
    ):
        self.db = db
        self.planner_runtime = planner_runtime or AIPlannerRuntime()
        self.validator = validator or PlannerValidator()
        self.conflict_resolver = conflict_resolver or PlannerConflictResolver()
        self.graph_builder = graph_builder or PlannerExecutionGraphBuilder()
        self.export_contract = export_contract or PlannerExportContract()
        self.asset_orchestrator = asset_orchestrator or AssetOrchestratorRuntime(db=db)
        self.diversity_guard = diversity_guard or PlannerDiversityGuard()
        self.optimizer = optimizer or PlannerOptimizer()
    def run(
        self,
        request: PlannerRequest,
    ) -> PlannerAssetExecutionResult:
        raw_plan = self.planner_runtime.build_plan(request)
        resolved_plan = self.conflict_resolver.resolve(raw_plan)
        resolved_plan = self.diversity_guard.apply(resolved_plan)
        resolved_plan = self.optimizer.optimize(resolved_plan)

        validation = self.validator.validate(resolved_plan)

        if not validation.valid:
            raise RuntimeError(
                f"Planner validation failed: {validation.to_dict()}"
            )

        graph = self.graph_builder.build(resolved_plan)
        planner_payload = self.export_contract.to_payload(
            plan=resolved_plan,
            graph=graph,
        )

        asset_plan_items = self.export_contract.to_asset_plan_items(resolved_plan)

        asset_result = self.asset_orchestrator.run(
            AssetOrchestrationRequest(
                production_id=request.context.production_id,
                plan_items=asset_plan_items,
                metadata={
                    "source": "planner_asset_orchestrator_integration",
                    "planner_version": resolved_plan.planner_version,
                    "execution_graph": graph.to_dict(),
                },
            )
        )

        return PlannerAssetExecutionResult(
            production_id=request.context.production_id,
            planner_payload=planner_payload,
            asset_result=asset_result,
            metadata={
                "validation": validation.to_dict(),
                "asset_plan_item_count": len(asset_plan_items),
                "asset_clip_count": len(asset_result.asset_clips),
                "failed_asset_count": len(asset_result.failed_items),
            },
        )