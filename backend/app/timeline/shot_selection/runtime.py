from __future__ import annotations

from app.timeline.semantic.models import TimelineSemanticAnalysis, TimelineSemanticSegment
from app.timeline.shot_selection.models import ShotSelection, ShotSelectionResult


class ShotSelectionRuntime:
    def select(
        self,
        analysis: TimelineSemanticAnalysis,
    ) -> ShotSelectionResult:
        shots = [
            self._select_segment_shot(segment)
            for segment in analysis.segments
        ]

        return ShotSelectionResult(
            production_id=analysis.production_id,
            shots=shots,
            metadata={
                "runtime": "ShotSelectionRuntime",
                "segment_count": len(analysis.segments),
                "shot_count": len(shots),
            },
        )

    def _select_segment_shot(
        self,
        segment: TimelineSemanticSegment,
    ) -> ShotSelection:
        segment_type = segment.segment_type.lower()
        emotion = segment.emotion.lower()
        pacing = segment.pacing.lower()
        visual_density = segment.visual_density.lower()

        if segment_type == "hook" or segment.viral_potential_score >= 0.9:
            return ShotSelection(
                segment_id=segment.segment_id,
                start_time=segment.start_time,
                end_time=segment.end_time,
                shot_type="broll_overlay",
                priority="critical",
                reason="hook/high viral potential needs strong visual interruption",
                asset_role="visual_support",
                motion_hint="zoom_in",
                transition_hint="impact_cut",
                metadata={
                    "segment_type": segment.segment_type,
                    "emotion": segment.emotion,
                    "pacing": segment.pacing,
                    "visual_density": segment.visual_density,
                },
            )

        if segment_type in {"solution", "main_point"} and visual_density in {"medium", "high"}:
            return ShotSelection(
                segment_id=segment.segment_id,
                start_time=segment.start_time,
                end_time=segment.end_time,
                shot_type="cutaway",
                priority="high",
                reason="solution/main point with b-roll should use cutaway shot",
                asset_role="visual_support",
                motion_hint="slow_push",
                transition_hint="smooth_cut",
                metadata={
                    "segment_type": segment.segment_type,
                    "emotion": segment.emotion,
                    "pacing": segment.pacing,
                    "visual_density": segment.visual_density,
                },
            )

        if segment_type == "cta":
            return ShotSelection(
                segment_id=segment.segment_id,
                start_time=segment.start_time,
                end_time=segment.end_time,
                shot_type="cta_screen",
                priority="high",
                reason="CTA segment should focus attention on action",
                asset_role="cta",
                motion_hint="scale_up",
                transition_hint="clean_cut",
                metadata={
                    "segment_type": segment.segment_type,
                    "emotion": segment.emotion,
                    "pacing": segment.pacing,
                    "visual_density": segment.visual_density,
                },
            )

        if emotion in {"surprised", "excited", "funny"} or pacing == "fast":
            return ShotSelection(
                segment_id=segment.segment_id,
                start_time=segment.start_time,
                end_time=segment.end_time,
                shot_type="reaction",
                priority="high",
                reason="high emotion/fast pacing should use reaction-style visual",
                asset_role="emphasis",
                motion_hint="pop_zoom",
                transition_hint="quick_cut",
                metadata={
                    "segment_type": segment.segment_type,
                    "emotion": segment.emotion,
                    "pacing": segment.pacing,
                    "visual_density": segment.visual_density,
                },
            )

        return ShotSelection(
            segment_id=segment.segment_id,
            start_time=segment.start_time,
            end_time=segment.end_time,
            shot_type="talking_head",
            priority="medium",
            reason="default shot keeps source video as primary visual",
            asset_role="primary",
            motion_hint="none",
            transition_hint="none",
            metadata={
                "segment_type": segment.segment_type,
                "emotion": segment.emotion,
                "pacing": segment.pacing,
                "visual_density": segment.visual_density,
            },
        )