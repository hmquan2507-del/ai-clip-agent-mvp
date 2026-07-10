from __future__ import annotations

from statistics import mean

from app.audio.beat_detection.models import BeatDetectionResult, BeatPoint
from app.subtitle.timing.models import SubtitleTimingResult
from app.timeline.motion_planning.models import MotionPlanningResult
from app.timeline.scene_rhythm.models import (
    SceneRhythmEvent,
    SceneRhythmResult,
    SceneRhythmSegment,
)
from app.timeline.semantic.models import (
    TimelineSemanticAnalysis,
    TimelineSemanticSegment,
)
from app.timeline.shot_selection.models import ShotSelectionResult
from app.timeline.transition_planning.models import TransitionPlanningResult


class SceneRhythmEngine:
    def __init__(
        self,
        max_beat_alignment_distance: float = 0.35,
        prefer_downbeat_for_transitions: bool = True,
    ):
        self.max_beat_alignment_distance = max_beat_alignment_distance
        self.prefer_downbeat_for_transitions = prefer_downbeat_for_transitions

    def build(
        self,
        analysis: TimelineSemanticAnalysis,
        subtitle_result: SubtitleTimingResult,
        beat_result: BeatDetectionResult,
        shot_result: ShotSelectionResult,
        motion_result: MotionPlanningResult,
        transition_result: TransitionPlanningResult,
    ) -> SceneRhythmResult:
        all_events: list[SceneRhythmEvent] = []
        rhythm_segments: list[SceneRhythmSegment] = []

        for segment in analysis.segments:
            segment_events = self._build_segment_events(
                segment=segment,
                subtitle_result=subtitle_result,
                beat_result=beat_result,
                shot_result=shot_result,
                motion_result=motion_result,
                transition_result=transition_result,
            )

            all_events.extend(segment_events)

            rhythm_segments.append(
                self._build_rhythm_segment(
                    segment=segment,
                    events=segment_events,
                    beat_result=beat_result,
                )
            )

        all_events.sort(
            key=lambda item: (
                item.aligned_time,
                item.event_type,
                item.event_id,
            )
        )

        return SceneRhythmResult(
            production_id=analysis.production_id,
            segments=rhythm_segments,
            events=all_events,
            metadata={
                "runtime": "SceneRhythmEngine",
                "segment_count": len(rhythm_segments),
                "event_count": len(all_events),
                "bpm": beat_result.bpm,
                "beat_provider": beat_result.provider_key,
                "max_beat_alignment_distance": self.max_beat_alignment_distance,
            },
        )

    def _build_segment_events(
        self,
        segment: TimelineSemanticSegment,
        subtitle_result: SubtitleTimingResult,
        beat_result: BeatDetectionResult,
        shot_result: ShotSelectionResult,
        motion_result: MotionPlanningResult,
        transition_result: TransitionPlanningResult,
    ) -> list[SceneRhythmEvent]:
        events: list[SceneRhythmEvent] = []

        shot = next(
            (
                item
                for item in shot_result.shots
                if item.segment_id == segment.segment_id
            ),
            None,
        )

        if shot is not None:
            events.append(
                self._align_event(
                    event_id=f"{segment.segment_id}_shot_start",
                    segment_id=segment.segment_id,
                    event_type="shot_start",
                    original_time=shot.start_time,
                    beat_result=beat_result,
                    prefer_downbeat=shot.priority == "critical",
                    metadata={
                        "shot_type": shot.shot_type,
                        "priority": shot.priority,
                    },
                )
            )

        for cue in subtitle_result.cues:
            if cue.segment_id != segment.segment_id:
                continue

            events.append(
                self._align_event(
                    event_id=f"{cue.cue_id}_start",
                    segment_id=segment.segment_id,
                    event_type="subtitle_start",
                    original_time=cue.start_time,
                    beat_result=beat_result,
                    prefer_downbeat=False,
                    metadata={
                        "cue_id": cue.cue_id,
                        "text": cue.text,
                        "importance_score": cue.importance_score,
                    },
                )
            )

        for motion in motion_result.motions:
            if motion.segment_id != segment.segment_id:
                continue

            events.append(
                self._align_event(
                    event_id=f"{segment.segment_id}_{motion.target_id}_motion",
                    segment_id=segment.segment_id,
                    event_type="motion_start",
                    original_time=motion.start_time,
                    beat_result=beat_result,
                    prefer_downbeat=motion.intensity == "high",
                    metadata={
                        "target_id": motion.target_id,
                        "motion_type": motion.motion_type,
                        "intensity": motion.intensity,
                    },
                )
            )

        for transition in transition_result.transitions:
            if transition.segment_id != segment.segment_id:
                continue

            events.append(
                self._align_event(
                    event_id=f"{segment.segment_id}_{transition.target_id}_transition",
                    segment_id=segment.segment_id,
                    event_type="transition",
                    original_time=transition.at_time,
                    beat_result=beat_result,
                    prefer_downbeat=self.prefer_downbeat_for_transitions,
                    metadata={
                        "target_id": transition.target_id,
                        "transition_type": transition.transition_type,
                        "duration": transition.duration,
                        "intensity": transition.intensity,
                    },
                )
            )

        return events

    def _align_event(
        self,
        event_id: str,
        segment_id: str,
        event_type: str,
        original_time: float,
        beat_result: BeatDetectionResult,
        prefer_downbeat: bool,
        metadata: dict,
    ) -> SceneRhythmEvent:
        beat = self._nearest_beat(
            beat_result=beat_result,
            target_time=original_time,
            prefer_downbeat=prefer_downbeat,
        )

        if beat is None:
            return SceneRhythmEvent(
                event_id=event_id,
                segment_id=segment_id,
                event_type=event_type,
                original_time=round(original_time, 3),
                aligned_time=round(original_time, 3),
                alignment_delta=0.0,
                metadata={
                    **metadata,
                    "beat_aligned": False,
                },
            )

        delta = beat.time - original_time

        return SceneRhythmEvent(
            event_id=event_id,
            segment_id=segment_id,
            event_type=event_type,
            original_time=round(original_time, 3),
            aligned_time=round(beat.time, 3),
            alignment_delta=round(delta, 3),
            beat_index=beat.beat_index,
            beat_strength=beat.strength,
            is_downbeat=beat.is_downbeat,
            metadata={
                **metadata,
                "beat_aligned": True,
            },
        )

    def _nearest_beat(
        self,
        beat_result: BeatDetectionResult,
        target_time: float,
        prefer_downbeat: bool,
    ) -> BeatPoint | None:
        candidates = beat_result.beats

        if prefer_downbeat:
            downbeats = [
                beat
                for beat in beat_result.beats
                if beat.is_downbeat
            ]

            if downbeats:
                candidates = downbeats

        if not candidates:
            return None

        nearest = min(
            candidates,
            key=lambda beat: abs(beat.time - target_time),
        )

        if abs(nearest.time - target_time) > self.max_beat_alignment_distance:
            return None

        return nearest

    def _build_rhythm_segment(
        self,
        segment: TimelineSemanticSegment,
        events: list[SceneRhythmEvent],
        beat_result: BeatDetectionResult,
    ) -> SceneRhythmSegment:
        beat_alignment_score = self._score_event_group(
            events=events,
            event_types={
                "shot_start",
                "motion_start",
                "transition",
                "subtitle_start",
            },
        )

        subtitle_alignment_score = self._score_event_group(
            events=events,
            event_types={"subtitle_start"},
        )

        motion_alignment_score = self._score_event_group(
            events=events,
            event_types={"motion_start"},
        )

        transition_alignment_score = self._score_event_group(
            events=events,
            event_types={"transition"},
        )

        energy = self._segment_energy(
            segment=segment,
            beat_result=beat_result,
        )

        overall_score = round(
            (
                beat_alignment_score * 0.35
                + subtitle_alignment_score * 0.20
                + motion_alignment_score * 0.20
                + transition_alignment_score * 0.25
            ),
            4,
        )

        return SceneRhythmSegment(
            segment_id=segment.segment_id,
            start_time=segment.start_time,
            end_time=segment.end_time,
            rhythm_type=self._rhythm_type(
                segment=segment,
                energy=energy,
            ),
            pacing=segment.pacing,
            energy=energy,
            beat_alignment_score=beat_alignment_score,
            subtitle_alignment_score=subtitle_alignment_score,
            motion_alignment_score=motion_alignment_score,
            transition_alignment_score=transition_alignment_score,
            overall_score=overall_score,
            events=events,
            metadata={
                "segment_type": segment.segment_type,
                "emotion": segment.emotion,
                "importance_score": segment.importance_score,
                "viral_potential_score": segment.viral_potential_score,
                "visual_density": segment.visual_density,
                "event_count": len(events),
            },
        )

    def _score_event_group(
        self,
        events: list[SceneRhythmEvent],
        event_types: set[str],
    ) -> float:
        selected = [
            event
            for event in events
            if event.event_type in event_types
        ]

        if not selected:
            return 1.0

        scores = []

        for event in selected:
            if not event.metadata.get("beat_aligned"):
                scores.append(0.5)
                continue

            distance = abs(event.alignment_delta)
            normalized = 1.0 - min(
                1.0,
                distance / self.max_beat_alignment_distance,
            )
            scores.append(normalized)

        return round(mean(scores), 4)

    def _segment_energy(
        self,
        segment: TimelineSemanticSegment,
        beat_result: BeatDetectionResult,
    ) -> float:
        overlapping_sections = [
            section
            for section in beat_result.sections
            if section.start_time < segment.end_time
            and segment.start_time < section.end_time
        ]

        if not overlapping_sections:
            return 0.5

        return round(
            mean(section.energy for section in overlapping_sections),
            4,
        )

    def _rhythm_type(
        self,
        segment: TimelineSemanticSegment,
        energy: float,
    ) -> str:
        if segment.segment_type == "hook":
            return "impact"

        if segment.segment_type == "cta":
            return "resolution"

        if segment.pacing == "fast" and energy >= 0.65:
            return "high_energy"

        if segment.pacing == "fast":
            return "quick"

        if energy >= 0.8:
            return "dynamic"

        return "steady"