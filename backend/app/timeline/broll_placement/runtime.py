from __future__ import annotations

from app.timeline.broll_placement.models import (
    BrollPlacement,
    BrollPlacementResult,
)
from app.timeline.semantic.models import TimelineSemanticAnalysis, TimelineSemanticAsset
from app.timeline.shot_selection.models import ShotSelectionResult, ShotSelection


class SmartBrollPlacementRuntime:
    def place(
        self,
        analysis: TimelineSemanticAnalysis,
        shot_result: ShotSelectionResult,
    ) -> BrollPlacementResult:
        placements: list[BrollPlacement] = []

        for shot in shot_result.shots:
            asset = self._find_best_broll_asset(
                analysis=analysis,
                shot=shot,
            )

            if asset is None:
                continue

            start_time, end_time = self._placement_window(
                shot=shot,
                asset=asset,
            )

            placements.append(
                BrollPlacement(
                    segment_id=shot.segment_id,
                    asset_id=asset.asset_id,
                    local_path=asset.local_path,
                    start_time=start_time,
                    end_time=end_time,
                    placement_type=self._placement_type(shot),
                    layer=2,
                    opacity=1.0,
                    motion_hint=shot.motion_hint,
                    transition_hint=shot.transition_hint,
                    reason=shot.reason,
                    metadata={
                        "shot_type": shot.shot_type,
                        "shot_priority": shot.priority,
                        "asset_title": asset.title,
                        "provider_key": asset.provider_key,
                        "asset_role": asset.role,
                    },
                )
            )

        return BrollPlacementResult(
            production_id=analysis.production_id,
            placements=placements,
            metadata={
                "runtime": "SmartBrollPlacementRuntime",
                "shot_count": len(shot_result.shots),
                "placement_count": len(placements),
            },
        )

    def _find_best_broll_asset(
        self,
        analysis: TimelineSemanticAnalysis,
        shot: ShotSelection,
    ) -> TimelineSemanticAsset | None:
        candidates = [
            asset
            for asset in analysis.assets
            if asset.asset_type == "broll"
            and self._overlaps(
                left_start=asset.start_time,
                left_end=asset.end_time,
                right_start=shot.start_time,
                right_end=shot.end_time,
            )
        ]

        if not candidates:
            return None

        candidates.sort(
            key=lambda asset: (
                0 if asset.role == shot.asset_role else 1,
                abs(asset.start_time - shot.start_time),
            )
        )

        return candidates[0]

    def _placement_window(
        self,
        shot: ShotSelection,
        asset: TimelineSemanticAsset,
    ) -> tuple[float, float]:
        segment_duration = max(0.0, shot.end_time - shot.start_time)

        if shot.shot_type == "broll_overlay":
            duration = min(segment_duration, 3.2)
            return shot.start_time, shot.start_time + duration

        if shot.shot_type == "cutaway":
            duration = min(segment_duration, 3.5)
            start = shot.start_time + min(0.5, segment_duration * 0.15)
            return start, min(start + duration, shot.end_time)

        if shot.shot_type == "cta_screen":
            duration = min(segment_duration, 4.0)
            start = max(shot.start_time, shot.end_time - duration)
            return start, shot.end_time

        duration = min(segment_duration, asset.end_time - asset.start_time)
        return shot.start_time, min(shot.start_time + duration, shot.end_time)

    def _placement_type(
        self,
        shot: ShotSelection,
    ) -> str:
        if shot.shot_type == "broll_overlay":
            return "overlay"

        if shot.shot_type == "cutaway":
            return "cutaway"

        if shot.shot_type == "cta_screen":
            return "cta_visual"

        return "supporting_visual"

    def _overlaps(
        self,
        left_start: float,
        left_end: float,
        right_start: float,
        right_end: float,
    ) -> bool:
        return left_start < right_end and right_start < left_end