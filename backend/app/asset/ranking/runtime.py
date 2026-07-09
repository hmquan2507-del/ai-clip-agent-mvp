from __future__ import annotations

from app.asset.ranking.license_policy import AssetLicensePolicy
from app.asset.ranking.models import (
    AssetRankingRequest,
    AssetRankingResponse,
    RankedAsset,
)
from app.asset.ranking.scoring import AssetScoringEngine


class AssetRankingRuntime:
    def __init__(
        self,
        scoring_engine: AssetScoringEngine | None = None,
        license_policy: AssetLicensePolicy | None = None,
    ):
        self.scoring_engine = scoring_engine or AssetScoringEngine()
        self.license_policy = license_policy or AssetLicensePolicy()

    def rank(
        self,
        request: AssetRankingRequest,
    ) -> AssetRankingResponse:
        accepted: list[RankedAsset] = []
        rejected: list[RankedAsset] = []

        for candidate in request.candidates:
            score, reasons, penalties = self.scoring_engine.score(
                query=request.query,
                asset=candidate,
                preferred_orientation=request.preferred_orientation,
                preferred_duration=request.preferred_duration,
            )

            ranked = RankedAsset(
                asset=candidate,
                score=score,
                reasons=reasons,
                penalties=penalties,
                metadata={
                    "provider_key": candidate.provider_key,
                    "provider_asset_id": candidate.provider_asset_id,
                    "license": candidate.license,
                },
            )

            if not self.license_policy.is_allowed(
                candidate.license,
                commercial_use=request.commercial_use,
            ):
                ranked.penalties.append(
                    self.license_policy.rejection_reason(candidate.license)
                )
                rejected.append(ranked)
                continue

            accepted.append(ranked)

        accepted.sort(key=lambda item: item.score, reverse=True)
        rejected.sort(key=lambda item: item.score, reverse=True)

        return AssetRankingResponse(
            query=request.query,
            asset_type=request.asset_type,
            ranked_assets=accepted[: request.limit],
            rejected_assets=rejected,
            metadata={
                "candidate_count": len(request.candidates),
                "accepted_count": len(accepted),
                "rejected_count": len(rejected),
                "limit": request.limit,
                "commercial_use": request.commercial_use,
            },
        )