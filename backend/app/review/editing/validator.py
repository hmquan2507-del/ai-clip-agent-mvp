from __future__ import annotations

from collections.abc import Iterable

from app.review.editing.enums import (
    EditableClipType,
    EditableTrackType,
    TimelineEditingIssueCode,
    TimelineOverlapPolicy,
)
from app.review.editing.models import (
    EditableTimeline,
    EditableTimelineClip,
    EditableTimelineTrack,
    TimelineEditingIssue,
    TimelineEditingValidationResult,
)


class TimelineEditingValidationError(
    ValueError
):
    def __init__(
        self,
        result: TimelineEditingValidationResult,
    ):
        self.result = result

        message = "; ".join(
            issue.message
            for issue in result.issues
        )

        super().__init__(
            message
            or "Timeline editing validation failed."
        )


class TimelineEditingValidator:
    TRACK_CLIP_COMPATIBILITY: dict[
        EditableTrackType,
        set[EditableClipType],
    ] = {
        EditableTrackType.VIDEO_PRIMARY: {
            EditableClipType.VIDEO,
        },
        EditableTrackType.VIDEO_OVERLAY: {
            EditableClipType.VIDEO,
            EditableClipType.BROLL,
            EditableClipType.EFFECT,
        },
        EditableTrackType.BROLL: {
            EditableClipType.BROLL,
            EditableClipType.VIDEO,
        },
        EditableTrackType.SUBTITLE: {
            EditableClipType.SUBTITLE,
        },
        EditableTrackType.MUSIC: {
            EditableClipType.MUSIC,
            EditableClipType.AUDIO,
        },
        EditableTrackType.SOUND_EFFECT: {
            EditableClipType.SOUND_EFFECT,
            EditableClipType.AUDIO,
        },
        EditableTrackType.VOICE: {
            EditableClipType.VOICE,
            EditableClipType.AUDIO,
        },
        EditableTrackType.AUDIO: {
            EditableClipType.AUDIO,
            EditableClipType.MUSIC,
            EditableClipType.SOUND_EFFECT,
            EditableClipType.VOICE,
        },
        EditableTrackType.EFFECT: {
            EditableClipType.EFFECT,
        },
        EditableTrackType.UNKNOWN: {
            EditableClipType.UNKNOWN,
        },
    }

    def validate_timeline(
        self,
        timeline: EditableTimeline,
    ) -> TimelineEditingValidationResult:
        issues: list[
            TimelineEditingIssue
        ] = []

        if not timeline.production_id:
            issues.append(
                TimelineEditingIssue(
                    code=(
                        TimelineEditingIssueCode
                        .TIMELINE_NOT_FOUND
                    ),
                    message=(
                        "Timeline production_id "
                        "is required."
                    ),
                )
            )

        track_ids: set[str] = set()
        clip_ids: set[str] = set()

        for track in timeline.tracks:
            if track.track_id in track_ids:
                issues.append(
                    TimelineEditingIssue(
                        code=(
                            TimelineEditingIssueCode
                            .TRACK_TYPE_MISMATCH
                        ),
                        message=(
                            "Duplicate track ID: "
                            f"{track.track_id}"
                        ),
                        track_id=track.track_id,
                    )
                )

            track_ids.add(
                track.track_id
            )

            for clip in track.clips:
                if clip.clip_id in clip_ids:
                    issues.append(
                        TimelineEditingIssue(
                            code=(
                                TimelineEditingIssueCode
                                .CLIP_ID_DUPLICATED
                            ),
                            message=(
                                "Duplicate clip ID: "
                                f"{clip.clip_id}"
                            ),
                            clip_id=clip.clip_id,
                            track_id=track.track_id,
                        )
                    )

                clip_ids.add(
                    clip.clip_id
                )

                result = self.validate_clip(
                    timeline=timeline,
                    track=track,
                    clip=clip,
                    ignore_clip_id=(
                        clip.clip_id
                    ),
                )

                issues.extend(
                    result.issues
                )

        return TimelineEditingValidationResult(
            valid=not issues,
            issues=tuple(issues),
            metadata={
                "track_count": (
                    timeline.track_count
                ),
                "clip_count": (
                    timeline.clip_count
                ),
            },
        )

    def validate_track_exists(
        self,
        timeline: EditableTimeline,
        track_id: str,
    ) -> TimelineEditingValidationResult:
        track = timeline.get_track(
            track_id
        )

        if track is not None:
            return self._success()

        return self._failure(
            TimelineEditingIssue(
                code=(
                    TimelineEditingIssueCode
                    .TRACK_NOT_FOUND
                ),
                message=(
                    "Timeline track does not exist: "
                    f"{track_id}"
                ),
                track_id=str(track_id),
            )
        )

    def validate_clip_exists(
        self,
        timeline: EditableTimeline,
        clip_id: str,
    ) -> TimelineEditingValidationResult:
        clip = timeline.get_clip(
            clip_id
        )

        if clip is not None:
            return self._success()

        return self._failure(
            TimelineEditingIssue(
                code=(
                    TimelineEditingIssueCode
                    .CLIP_NOT_FOUND
                ),
                message=(
                    "Timeline clip does not exist: "
                    f"{clip_id}"
                ),
                clip_id=str(clip_id),
            )
        )

    def validate_track_editable(
        self,
        track: EditableTimelineTrack,
    ) -> TimelineEditingValidationResult:
        if not track.locked:
            return self._success()

        return self._failure(
            TimelineEditingIssue(
                code=(
                    TimelineEditingIssueCode
                    .TRACK_LOCKED
                ),
                message=(
                    "Timeline track is locked: "
                    f"{track.track_id}"
                ),
                track_id=track.track_id,
            )
        )

    def validate_clip(
        self,
        *,
        timeline: EditableTimeline,
        track: EditableTimelineTrack,
        clip: EditableTimelineClip,
        ignore_clip_id: str | None = None,
    ) -> TimelineEditingValidationResult:
        issues: list[
            TimelineEditingIssue
        ] = []

        issues.extend(
            self.validate_clip_range(
                timeline=timeline,
                clip=clip,
            ).issues
        )

        issues.extend(
            self.validate_source_range(
                clip=clip
            ).issues
        )

        issues.extend(
            self.validate_track_accepts_clip(
                track=track,
                clip=clip,
            ).issues
        )

        issues.extend(
            self.validate_overlap(
                track=track,
                candidate=clip,
                ignore_clip_id=(
                    ignore_clip_id
                ),
            ).issues
        )

        if clip.track_id != track.track_id:
            issues.append(
                TimelineEditingIssue(
                    code=(
                        TimelineEditingIssueCode
                        .CLIP_TRACK_MISMATCH
                    ),
                    message=(
                        "Clip track_id does not "
                        "match target track."
                    ),
                    clip_id=clip.clip_id,
                    track_id=track.track_id,
                    metadata={
                        "clip_track_id": (
                            clip.track_id
                        ),
                    },
                )
            )

        return TimelineEditingValidationResult(
            valid=not issues,
            issues=tuple(issues),
        )

    def validate_clip_range(
        self,
        *,
        timeline: EditableTimeline,
        clip: EditableTimelineClip,
    ) -> TimelineEditingValidationResult:
        issues: list[
            TimelineEditingIssue
        ] = []

        if (
            clip.start_time < 0
            or clip.end_time < 0
        ):
            issues.append(
                TimelineEditingIssue(
                    code=(
                        TimelineEditingIssueCode
                        .NEGATIVE_TIME
                    ),
                    message=(
                        "Clip timeline time cannot "
                        "be negative."
                    ),
                    clip_id=clip.clip_id,
                    track_id=clip.track_id,
                )
            )

        if clip.end_time <= clip.start_time:
            issues.append(
                TimelineEditingIssue(
                    code=(
                        TimelineEditingIssueCode
                        .INVALID_TIMELINE_RANGE
                    ),
                    message=(
                        "Clip end_time must be "
                        "greater than start_time."
                    ),
                    clip_id=clip.clip_id,
                    track_id=clip.track_id,
                )
            )

        if (
            clip.duration
            + 1e-9
            < timeline.minimum_clip_duration
        ):
            issues.append(
                TimelineEditingIssue(
                    code=(
                        TimelineEditingIssueCode
                        .CLIP_TOO_SHORT
                    ),
                    message=(
                        "Clip duration is shorter "
                        "than one timeline frame."
                    ),
                    clip_id=clip.clip_id,
                    track_id=clip.track_id,
                    metadata={
                        "duration": clip.duration,
                        "minimum_duration": (
                            timeline
                            .minimum_clip_duration
                        ),
                    },
                )
            )

        return TimelineEditingValidationResult(
            valid=not issues,
            issues=tuple(issues),
        )

    def validate_source_range(
        self,
        *,
        clip: EditableTimelineClip,
    ) -> TimelineEditingValidationResult:
        issues: list[
            TimelineEditingIssue
        ] = []

        if (
            clip.source_start is None
            and clip.source_end is None
        ):
            return self._success()

        if (
            clip.source_start is None
            or clip.source_end is None
        ):
            issues.append(
                TimelineEditingIssue(
                    code=(
                        TimelineEditingIssueCode
                        .INVALID_SOURCE_RANGE
                    ),
                    message=(
                        "source_start and source_end "
                        "must be provided together."
                    ),
                    clip_id=clip.clip_id,
                    track_id=clip.track_id,
                )
            )

            return TimelineEditingValidationResult(
                valid=False,
                issues=tuple(issues),
            )

        if (
            clip.source_start < 0
            or clip.source_end < 0
        ):
            issues.append(
                TimelineEditingIssue(
                    code=(
                        TimelineEditingIssueCode
                        .NEGATIVE_TIME
                    ),
                    message=(
                        "Clip source time cannot "
                        "be negative."
                    ),
                    clip_id=clip.clip_id,
                    track_id=clip.track_id,
                )
            )

        if (
            clip.source_end
            <= clip.source_start
        ):
            issues.append(
                TimelineEditingIssue(
                    code=(
                        TimelineEditingIssueCode
                        .INVALID_SOURCE_RANGE
                    ),
                    message=(
                        "source_end must be greater "
                        "than source_start."
                    ),
                    clip_id=clip.clip_id,
                    track_id=clip.track_id,
                )
            )

        if (
            clip.source_duration
            is not None
            and clip.source_end
            > clip.source_duration + 1e-9
        ):
            issues.append(
                TimelineEditingIssue(
                    code=(
                        TimelineEditingIssueCode
                        .SOURCE_DURATION_EXCEEDED
                    ),
                    message=(
                        "Clip source_end exceeds "
                        "the source media duration."
                    ),
                    clip_id=clip.clip_id,
                    track_id=clip.track_id,
                    metadata={
                        "source_end": (
                            clip.source_end
                        ),
                        "source_duration": (
                            clip.source_duration
                        ),
                    },
                )
            )

        return TimelineEditingValidationResult(
            valid=not issues,
            issues=tuple(issues),
        )

    def validate_track_accepts_clip(
        self,
        *,
        track: EditableTimelineTrack,
        clip: EditableTimelineClip,
    ) -> TimelineEditingValidationResult:
        accepted_types = (
            self.TRACK_CLIP_COMPATIBILITY.get(
                track.track_type,
                {
                    EditableClipType.UNKNOWN,
                },
            )
        )

        if clip.clip_type in accepted_types:
            return self._success()

        return self._failure(
            TimelineEditingIssue(
                code=(
                    TimelineEditingIssueCode
                    .TRACK_TYPE_MISMATCH
                ),
                message=(
                    "Track does not accept this "
                    "clip type."
                ),
                clip_id=clip.clip_id,
                track_id=track.track_id,
                metadata={
                    "track_type": (
                        track.track_type.value
                    ),
                    "clip_type": (
                        clip.clip_type.value
                    ),
                    "accepted_clip_types": [
                        item.value
                        for item
                        in accepted_types
                    ],
                },
            )
        )

    def validate_overlap(
        self,
        *,
        track: EditableTimelineTrack,
        candidate: EditableTimelineClip,
        ignore_clip_id: str | None = None,
    ) -> TimelineEditingValidationResult:
        if (
            track.overlap_policy
            == TimelineOverlapPolicy.ALLOW
        ):
            return self._success()

        conflicts = [
            clip
            for clip in track.clips
            if (
                clip.clip_id
                != ignore_clip_id
                and self._ranges_overlap(
                    candidate.start_time,
                    candidate.end_time,
                    clip.start_time,
                    clip.end_time,
                )
            )
        ]

        if not conflicts:
            return self._success()

        return self._failure(
            TimelineEditingIssue(
                code=(
                    TimelineEditingIssueCode
                    .CLIP_OVERLAP
                ),
                message=(
                    "Clip overlaps another clip "
                    "on a non-overlapping track."
                ),
                clip_id=candidate.clip_id,
                track_id=track.track_id,
                metadata={
                    "conflicting_clip_ids": [
                        clip.clip_id
                        for clip in conflicts
                    ],
                    "candidate_start": (
                        candidate.start_time
                    ),
                    "candidate_end": (
                        candidate.end_time
                    ),
                },
            )
        )

    def validate_move(
        self,
        *,
        timeline: EditableTimeline,
        clip_id: str,
        target_track_id: str,
        new_start_time: float,
    ) -> TimelineEditingValidationResult:
        source_clip = timeline.get_clip(
            clip_id
        )
        target_track = timeline.get_track(
            target_track_id
        )

        issues: list[
            TimelineEditingIssue
        ] = []

        if source_clip is None:
            issues.extend(
                self.validate_clip_exists(
                    timeline,
                    clip_id,
                ).issues
            )

        if target_track is None:
            issues.extend(
                self.validate_track_exists(
                    timeline,
                    target_track_id,
                ).issues
            )

        if issues:
            return TimelineEditingValidationResult(
                valid=False,
                issues=tuple(issues),
            )

        issues.extend(
            self.validate_track_editable(
                target_track
            ).issues
        )

        duration = source_clip.duration

        candidate = source_clip.clone()
        candidate.track_id = (
            target_track.track_id
        )
        candidate.start_time = float(
            new_start_time
        )
        candidate.end_time = (
            candidate.start_time
            + duration
        )

        issues.extend(
            self.validate_clip(
                timeline=timeline,
                track=target_track,
                clip=candidate,
                ignore_clip_id=clip_id,
            ).issues
        )

        return TimelineEditingValidationResult(
            valid=not issues,
            issues=tuple(issues),
            metadata={
                "candidate": (
                    candidate.to_dict()
                ),
            },
        )

    def validate_trim_start(
        self,
        *,
        timeline: EditableTimeline,
        clip_id: str,
        new_start_time: float,
    ) -> TimelineEditingValidationResult:
        return self._validate_trim(
            timeline=timeline,
            clip_id=clip_id,
            new_start_time=new_start_time,
            new_end_time=None,
        )

    def validate_trim_end(
        self,
        *,
        timeline: EditableTimeline,
        clip_id: str,
        new_end_time: float,
    ) -> TimelineEditingValidationResult:
        return self._validate_trim(
            timeline=timeline,
            clip_id=clip_id,
            new_start_time=None,
            new_end_time=new_end_time,
        )

    def validate_insert(
        self,
        *,
        timeline: EditableTimeline,
        track_id: str,
        clip: EditableTimelineClip,
    ) -> TimelineEditingValidationResult:
        issues: list[
            TimelineEditingIssue
        ] = []

        track = timeline.get_track(
            track_id
        )

        if track is None:
            return self.validate_track_exists(
                timeline,
                track_id,
            )

        if timeline.get_clip(
            clip.clip_id
        ) is not None:
            issues.append(
                TimelineEditingIssue(
                    code=(
                        TimelineEditingIssueCode
                        .CLIP_ID_DUPLICATED
                    ),
                    message=(
                        "Clip ID already exists: "
                        f"{clip.clip_id}"
                    ),
                    clip_id=clip.clip_id,
                    track_id=track_id,
                )
            )

        issues.extend(
            self.validate_track_editable(
                track
            ).issues
        )

        candidate = clip.clone()
        candidate.track_id = track_id

        issues.extend(
            self.validate_clip(
                timeline=timeline,
                track=track,
                clip=candidate,
                ignore_clip_id=None,
            ).issues
        )

        return TimelineEditingValidationResult(
            valid=not issues,
            issues=tuple(issues),
            metadata={
                "candidate": (
                    candidate.to_dict()
                ),
            },
        )

    def require_valid(
        self,
        result: TimelineEditingValidationResult,
    ) -> None:
        if not result.valid:
            raise TimelineEditingValidationError(
                result
            )

    def _validate_trim(
        self,
        *,
        timeline: EditableTimeline,
        clip_id: str,
        new_start_time: float | None,
        new_end_time: float | None,
    ) -> TimelineEditingValidationResult:
        clip = timeline.get_clip(
            clip_id
        )
        track = timeline.find_clip_track(
            clip_id
        )

        if clip is None:
            return self.validate_clip_exists(
                timeline,
                clip_id,
            )

        if track is None:
            return self.validate_track_exists(
                timeline,
                clip.track_id,
            )

        issues = list(
            self.validate_track_editable(
                track
            ).issues
        )

        candidate = clip.clone()

        if new_start_time is not None:
            delta = (
                float(new_start_time)
                - candidate.start_time
            )

            candidate.start_time = float(
                new_start_time
            )

            if (
                candidate.source_start
                is not None
            ):
                candidate.source_start += (
                    delta
                )

        if new_end_time is not None:
            delta = (
                candidate.end_time
                - float(new_end_time)
            )

            candidate.end_time = float(
                new_end_time
            )

            if (
                candidate.source_end
                is not None
            ):
                candidate.source_end -= (
                    delta
                )

        issues.extend(
            self.validate_clip(
                timeline=timeline,
                track=track,
                clip=candidate,
                ignore_clip_id=clip_id,
            ).issues
        )

        return TimelineEditingValidationResult(
            valid=not issues,
            issues=tuple(issues),
            metadata={
                "candidate": (
                    candidate.to_dict()
                ),
            },
        )

    def _ranges_overlap(
        self,
        start_a: float,
        end_a: float,
        start_b: float,
        end_b: float,
    ) -> bool:
        return (
            start_a < end_b
            and start_b < end_a
        )

    def _success(
        self,
    ) -> TimelineEditingValidationResult:
        return TimelineEditingValidationResult(
            valid=True
        )

    def _failure(
        self,
        *issues: TimelineEditingIssue,
    ) -> TimelineEditingValidationResult:
        return TimelineEditingValidationResult(
            valid=False,
            issues=tuple(issues),
        )