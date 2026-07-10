from __future__ import annotations

from collections import defaultdict
from typing import Any

from app.subtitle.timing.models import SubtitleTimingResult
from app.timeline.broll_placement.models import BrollPlacementResult
from app.timeline.camera_movement.models import CameraMovementResult
from app.timeline.finalizer.models import (
    FinalTimeline,
    FinalTimelineClip,
    FinalTimelineEffect,
    FinalTimelineTrack,
    FinalTimelineTransition,
)
from app.timeline.scene_rhythm.models import SceneRhythmResult
from app.timeline.semantic.models import TimelineSemanticAnalysis
from app.timeline.transition_planning.models import (
    TransitionPlanningResult,
)


class TimelineFinalizerRuntime:
    def __init__(
        self,
        width: int = 1080,
        height: int = 1920,
        fps: float = 30.0,
    ):
        self.width = width
        self.height = height
        self.fps = fps

    def finalize(
        self,
        analysis: TimelineSemanticAnalysis,
        broll_result: BrollPlacementResult,
        subtitle_result: SubtitleTimingResult,
        camera_result: CameraMovementResult,
        transition_result: TransitionPlanningResult,
        rhythm_result: SceneRhythmResult,
    ) -> FinalTimeline:
        clips: list[FinalTimelineClip] = []

        clips.extend(
            self._build_source_clips(
                analysis=analysis,
            )
        )

        clips.extend(
            self._build_broll_clips(
                broll_result=broll_result,
            )
        )

        clips.extend(
            self._build_audio_clips(
                analysis=analysis,
            )
        )

        clips.extend(
            self._build_subtitle_clips(
                subtitle_result=subtitle_result,
            )
        )

        clips = self._normalize_clips(clips)
        clips = self._resolve_clip_conflicts(clips)

        tracks = self._build_tracks(clips)

        effects = self._build_camera_effects(
            camera_result=camera_result,
            rhythm_result=rhythm_result,
            broll_result=broll_result,
        )

        transitions = self._build_transitions(
            transition_result=transition_result,
            rhythm_result=rhythm_result,
            broll_result=broll_result,
        )

        duration = self._calculate_duration(
            analysis=analysis,
            clips=clips,
        )

        return FinalTimeline(
            production_id=analysis.production_id,
            version="14.11.0",
            duration=duration,
            width=self.width,
            height=self.height,
            fps=self.fps,
            tracks=tracks,
            effects=effects,
            transitions=transitions,
            metadata={
                "runtime": "TimelineFinalizerRuntime",
                "semantic_segment_count": len(analysis.segments),
                "track_count": len(tracks),
                "clip_count": len(clips),
                "effect_count": len(effects),
                "transition_count": len(transitions),
                "rhythm_segment_count": len(rhythm_result.segments),
                "single_source_of_truth": True,
            },
        )

    def _build_source_clips(
        self,
        analysis: TimelineSemanticAnalysis,
    ) -> list[FinalTimelineClip]:
        clips: list[FinalTimelineClip] = []

        for segment in analysis.segments:
            clips.append(
                FinalTimelineClip(
                    clip_id=f"{segment.segment_id}_source",
                    track_type="video_primary",
                    start_time=segment.start_time,
                    end_time=segment.end_time,
                    layer=1,
                    metadata={
                        "segment_id": segment.segment_id,
                        "segment_type": segment.segment_type,
                        "emotion": segment.emotion,
                        "pacing": segment.pacing,
                        "importance_score": segment.importance_score,
                        "viral_potential_score": (
                            segment.viral_potential_score
                        ),
                        "source": "semantic_timeline",
                    },
                )
            )

        return clips

    def _build_broll_clips(
        self,
        broll_result: BrollPlacementResult,
    ) -> list[FinalTimelineClip]:
        clips: list[FinalTimelineClip] = []

        for placement in broll_result.placements:
            clips.append(
                FinalTimelineClip(
                    clip_id=f"{placement.segment_id}_{placement.asset_id}",
                    track_type="broll",
                    start_time=placement.start_time,
                    end_time=placement.end_time,
                    layer=placement.layer,
                    asset_id=placement.asset_id,
                    local_path=placement.local_path,
                    opacity=placement.opacity,
                    metadata={
                        **placement.metadata,
                        "segment_id": placement.segment_id,
                        "placement_type": placement.placement_type,
                        "motion_hint": placement.motion_hint,
                        "transition_hint": placement.transition_hint,
                        "reason": placement.reason,
                        "source": "smart_broll_placement",
                    },
                )
            )

        return clips

    def _build_audio_clips(
        self,
        analysis: TimelineSemanticAnalysis,
    ) -> list[FinalTimelineClip]:
        clips: list[FinalTimelineClip] = []

        for asset in analysis.assets:
            if asset.asset_type not in {
                "music",
                "sound_effect",
            }:
                continue

            track_type = (
                "music"
                if asset.asset_type == "music"
                else "sfx"
            )

            default_volume = (
                0.18
                if track_type == "music"
                else 0.75
            )

            clips.append(
                FinalTimelineClip(
                    clip_id=f"{track_type}_{asset.asset_id}",
                    track_type=track_type,
                    start_time=asset.start_time,
                    end_time=asset.end_time,
                    layer=1 if track_type == "music" else 2,
                    asset_id=asset.asset_id,
                    local_path=asset.local_path,
                    volume=default_volume,
                    metadata={
                        **asset.metadata,
                        "provider_key": asset.provider_key,
                        "title": asset.title,
                        "asset_role": asset.role,
                        "source": "semantic_asset",
                    },
                )
            )

        return clips

    def _build_subtitle_clips(
        self,
        subtitle_result: SubtitleTimingResult,
    ) -> list[FinalTimelineClip]:
        clips: list[FinalTimelineClip] = []

        for cue in subtitle_result.cues:
            clips.append(
                FinalTimelineClip(
                    clip_id=cue.cue_id,
                    track_type="subtitle",
                    start_time=cue.start_time,
                    end_time=cue.end_time,
                    layer=10,
                    content=cue.text,
                    metadata={
                        **cue.metadata,
                        "segment_id": cue.segment_id,
                        "word_count": cue.word_count,
                        "characters_per_second": (
                            cue.characters_per_second
                        ),
                        "importance_score": cue.importance_score,
                        "highlight_words": cue.highlight_words,
                        "source": "subtitle_timing_optimizer",
                    },
                )
            )

        return clips

    def _build_camera_effects(
        self,
        camera_result: CameraMovementResult,
        rhythm_result: SceneRhythmResult,
        broll_result: BrollPlacementResult,
    ) -> list[FinalTimelineEffect]:
        effects: list[FinalTimelineEffect] = []

        for movement in camera_result.movements:
            aligned_start = self._aligned_event_time(
            rhythm_result=rhythm_result,
            segment_id=movement.segment_id,
            event_type="motion_start",
            fallback=movement.start_time,
        )

        timeline_target_id = self._resolve_timeline_target_id(
            target_id=movement.target_id,
            segment_id=movement.segment_id,
            broll_result=broll_result,
        )

        effects.append(
            FinalTimelineEffect(
                effect_id=(
                    f"{movement.segment_id}_"
                    f"{movement.target_id}_camera"
                ),
                target_id=timeline_target_id,
                effect_type="camera_movement",
                start_time=aligned_start,
                end_time=movement.end_time,
                parameters={
                    "movement_type": movement.movement_type,
                    "crop_mode": movement.crop_mode,
                    "scale_from": movement.scale_from,
                    "scale_to": movement.scale_to,
                    "x_from": movement.x_from,
                    "y_from": movement.y_from,
                    "x_to": movement.x_to,
                    "y_to": movement.y_to,
                },
                metadata={
                    **movement.metadata,
                    "segment_id": movement.segment_id,
                    "original_target_id": movement.target_id,
                    "resolved_target_id": timeline_target_id,
                    "rhythm_aligned": (
                        aligned_start != movement.start_time
                    ),
                },
            )
        )

        return effects

    def _build_transitions(
        self,
        transition_result: TransitionPlanningResult,
        rhythm_result: SceneRhythmResult,
        broll_result: BrollPlacementResult,
    ) -> list[FinalTimelineTransition]:
        transitions: list[FinalTimelineTransition] = []

        for transition in transition_result.transitions:
            aligned_time = self._aligned_event_time(
                rhythm_result=rhythm_result,
                segment_id=transition.segment_id,
                event_type="transition",
                fallback=transition.at_time,
        )

        timeline_target_id = self._resolve_timeline_target_id(
            target_id=transition.target_id,
            segment_id=transition.segment_id,
            broll_result=broll_result,
        )

        transitions.append(
            FinalTimelineTransition(
                transition_id=(
                    f"{transition.segment_id}_"
                    f"{transition.target_id}_transition"
                ),
                target_id=timeline_target_id,
                transition_type=transition.transition_type,
                at_time=aligned_time,
                duration=transition.duration,
                parameters={
                    "intensity": transition.intensity,
                },
                metadata={
                    **transition.metadata,
                    "segment_id": transition.segment_id,
                    "original_target_id": transition.target_id,
                    "resolved_target_id": timeline_target_id,
                    "original_time": transition.at_time,
                    "rhythm_aligned": (
                        aligned_time != transition.at_time
                    ),
                },
            )
        )

        return transitions

    def _normalize_clips(
        self,
        clips: list[FinalTimelineClip],
    ) -> list[FinalTimelineClip]:
        normalized: list[FinalTimelineClip] = []

        for clip in clips:
            start_time = max(0.0, float(clip.start_time))
            end_time = max(start_time, float(clip.end_time))

            if end_time <= start_time:
                continue

            clip.start_time = round(start_time, 3)
            clip.end_time = round(end_time, 3)
            clip.layer = max(1, int(clip.layer))

            normalized.append(clip)

        return normalized

    def _resolve_clip_conflicts(
        self,
        clips: list[FinalTimelineClip],
    ) -> list[FinalTimelineClip]:
        resolved: list[FinalTimelineClip] = []

        ordered = sorted(
            clips,
            key=lambda clip: (
                clip.start_time,
                clip.track_type,
                clip.layer,
                clip.clip_id,
            ),
        )

        for clip in ordered:
            if clip.track_type in {
                "music",
                "subtitle",
                "video_primary",
            }:
                resolved.append(clip)
                continue

            conflicting_layers = {
                existing.layer
                for existing in resolved
                if existing.track_type == clip.track_type
                and self._overlaps(existing, clip)
            }

            while clip.layer in conflicting_layers:
                clip.layer += 1
                clip.metadata = {
                    **clip.metadata,
                    "layer_conflict_resolved": True,
                }

            resolved.append(clip)

        return resolved

    def _build_tracks(
        self,
        clips: list[FinalTimelineClip],
    ) -> list[FinalTimelineTrack]:
        groups: dict[
            tuple[str, int],
            list[FinalTimelineClip],
        ] = defaultdict(list)

        for clip in clips:
            groups[(clip.track_type, clip.layer)].append(clip)

        tracks: list[FinalTimelineTrack] = []

        for track_index, (
            (track_type, layer),
            track_clips,
        ) in enumerate(
            sorted(
                groups.items(),
                key=lambda item: (
                    item[0][1],
                    item[0][0],
                ),
            ),
            start=1,
        ):
            track_clips.sort(
                key=lambda clip: (
                    clip.start_time,
                    clip.end_time,
                    clip.clip_id,
                )
            )

            tracks.append(
                FinalTimelineTrack(
                    track_id=(
                        f"track_{track_index}_"
                        f"{track_type}_{layer}"
                    ),
                    track_type=track_type,
                    layer=layer,
                    clips=track_clips,
                    metadata={
                        "clip_count": len(track_clips),
                    },
                )
            )

        return tracks

    def _calculate_duration(
        self,
        analysis: TimelineSemanticAnalysis,
        clips: list[FinalTimelineClip],
    ) -> float:
        values = [
            segment.end_time
            for segment in analysis.segments
        ]

        values.extend(
            clip.end_time
            for clip in clips
        )

        return round(max(values, default=0.0), 3)

    def _aligned_event_time(
        self,
        rhythm_result: SceneRhythmResult,
        segment_id: str,
        event_type: str,
        fallback: float,
    ) -> float:
        matching = [
            event
            for event in rhythm_result.events
            if event.segment_id == segment_id
            and event.event_type == event_type
        ]

        if not matching:
            return round(fallback, 3)

        nearest = min(
            matching,
            key=lambda event: abs(
                event.original_time - fallback
            ),
        )

        return round(nearest.aligned_time, 3)

    def _overlaps(
        self,
        left: FinalTimelineClip,
        right: FinalTimelineClip,
    ) -> bool:
        return (
            left.start_time < right.end_time
            and right.start_time < left.end_time
        )
    
    def _resolve_timeline_target_id(
        self,
        target_id: str,
        segment_id: str,
        broll_result: BrollPlacementResult,
    ) -> str:
        for placement in broll_result.placements:
            if (
            placement.asset_id == target_id
            and placement.segment_id == segment_id
            ):
                return f"{placement.segment_id}_{placement.asset_id}"

        return target_id