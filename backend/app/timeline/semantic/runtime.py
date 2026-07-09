from __future__ import annotations

from app.timeline.semantic.models import (
    TimelineSemanticAnalysis,
    TimelineSemanticAsset,
    TimelineSemanticSegment,
)


class TimelineSemanticEngine:
    def analyze(
        self,
        production_id: str,
        planner_payload: dict,
        asset_result: dict,
    ) -> TimelineSemanticAnalysis:
        segments = self._extract_segments(planner_payload)
        assets = self._extract_assets(asset_result)

        enriched_segments = [
            self._enrich_segment(segment=segment, assets=assets)
            for segment in segments
        ]

        return TimelineSemanticAnalysis(
            production_id=production_id,
            segments=enriched_segments,
            assets=assets,
            metadata={
                "semantic_engine": "TimelineSemanticEngine",
                "segment_count": len(enriched_segments),
                "asset_count": len(assets),
            },
        )

    def _extract_segments(self, planner_payload: dict) -> list[TimelineSemanticSegment]:
        instructions = (
            planner_payload
            .get("planner_payload", {})
            .get("plan", {})
            .get("instructions", [])
        )

        segment_map: dict[str, TimelineSemanticSegment] = {}

        for instruction in instructions:
            metadata = instruction.get("metadata") or {}
            segment_id = metadata.get("segment_id")

            if not segment_id:
                continue

            if segment_id not in segment_map:
                segment_map[segment_id] = TimelineSemanticSegment(
                    segment_id=segment_id,
                    start_time=float(instruction.get("start_time") or 0),
                    end_time=float(instruction.get("end_time") or 0),
                    segment_type=metadata.get("segment_type", "main_point"),
                    emotion=metadata.get("emotion", "neutral"),
                    metadata={
                        "source": "planner_payload",
                    },
                )

            segment = segment_map[segment_id]
            segment.start_time = min(segment.start_time, float(instruction.get("start_time") or segment.start_time))
            segment.end_time = max(segment.end_time, float(instruction.get("end_time") or segment.end_time))

        return list(segment_map.values())

    def _extract_assets(self, asset_result: dict) -> list[TimelineSemanticAsset]:
        clips = (
            asset_result
            .get("asset_result", {})
            .get("asset_clips", [])
        )

        assets: list[TimelineSemanticAsset] = []

        for clip in clips:
            metadata = clip.get("metadata") or {}

            assets.append(
                TimelineSemanticAsset(
                    asset_id=str(clip.get("asset_id")),
                    asset_type=clip.get("asset_type"),
                    track_type=clip.get("track_type"),
                    start_time=float(clip.get("start_time") or 0),
                    end_time=float(clip.get("end_time") or 0),
                    local_path=clip.get("local_path"),
                    provider_key=metadata.get("provider_key"),
                    title=clip.get("title"),
                    role=self._infer_asset_role(clip),
                    metadata=metadata,
                )
            )

        return assets

    def _enrich_segment(
        self,
        segment: TimelineSemanticSegment,
        assets: list[TimelineSemanticAsset],
    ) -> TimelineSemanticSegment:
        overlapping_assets = [
            asset for asset in assets
            if asset.start_time < segment.end_time and segment.start_time < asset.end_time
        ]

        broll_count = sum(1 for asset in overlapping_assets if asset.asset_type == "broll")
        sfx_count = sum(1 for asset in overlapping_assets if asset.asset_type == "sound_effect")

        segment.visual_density = self._visual_density(broll_count)
        segment.pacing = self._pacing(segment, broll_count, sfx_count)
        segment.metadata = {
            **segment.metadata,
            "overlapping_asset_count": len(overlapping_assets),
            "broll_count": broll_count,
            "sfx_count": sfx_count,
        }

        return segment

    def _infer_asset_role(self, clip: dict) -> str:
        asset_type = clip.get("asset_type")

        if asset_type == "music":
            return "background"

        if asset_type == "sound_effect":
            return "emphasis"

        if asset_type == "broll":
            return "visual_support"

        return "supporting"

    def _visual_density(self, broll_count: int) -> str:
        if broll_count <= 0:
            return "low"

        if broll_count == 1:
            return "medium"

        return "high"

    def _pacing(
        self,
        segment: TimelineSemanticSegment,
        broll_count: int,
        sfx_count: int,
    ) -> str:
        if segment.duration <= 3 or sfx_count >= 1:
            return "fast"

        if broll_count >= 2:
            return "dynamic"

        return "normal"