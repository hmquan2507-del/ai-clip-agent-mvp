from __future__ import annotations

from copy import deepcopy
from typing import Any
from uuid import uuid4

from app.review.editing.enums import (
    TimelineEditingOperationType,
)
from app.review.editing.models import (
    EditableTimeline,
    EditableTimelineClip,
    EditableTimelineTrack,
    TimelineEditingEvent,
    TimelineEditingValidationResult,
    TimelineMutationResult,
)
from app.review.editing.validator import (
    TimelineEditingValidator,
)


class TimelineMutationRuntime:
    def __init__(
        self,
        timeline: EditableTimeline,
        *,
        validator: TimelineEditingValidator | None = None,
    ):
        self._timeline = timeline.clone()
        self._original_timeline = timeline.clone()

        self.validator = (
            validator
            or TimelineEditingValidator()
        )

        self._events: list[
            TimelineEditingEvent
        ] = []

    @property
    def timeline(self) -> EditableTimeline:
        return self._timeline.clone()

    @property
    def original_timeline(
        self,
    ) -> EditableTimeline:
        return self._original_timeline.clone()

    @property
    def events(
        self,
    ) -> list[TimelineEditingEvent]:
        return list(self._events)

    def snapshot(
        self,
    ) -> EditableTimeline:
        return self.timeline

    def replace_timeline(
        self,
        timeline: EditableTimeline,
        *,
        clear_events: bool = False,
    ) -> EditableTimeline:
        self._timeline = timeline.clone()

        if clear_events:
            self._events.clear()

        return self.timeline

    def move_clip(
        self,
        clip_id: str,
        new_start_time: float,
        *,
        target_track_id: str | None = None,
    ) -> TimelineMutationResult:
        clip = self._timeline.get_clip(
            clip_id
        )

        source_track = (
            self._timeline.find_clip_track(
                clip_id
            )
        )

        if clip is None or source_track is None:
            return self._failure(
                f"Timeline clip does not exist: {clip_id}"
            )

        target_track_id = (
            target_track_id
            or source_track.track_id
        )

        validation = (
            self.validator.validate_move(
                timeline=self._timeline,
                clip_id=clip_id,
                target_track_id=(
                    target_track_id
                ),
                new_start_time=(
                    new_start_time
                ),
            )
        )

        if not validation.valid:
            return self._validation_failure(
                validation
            )

        before = clip.to_dict()
        duration = clip.duration

        target_track = (
            self._timeline.get_track(
                target_track_id
            )
        )

        if target_track is None:
            return self._failure(
                "Target track does not exist."
            )

        source_track.remove_clip(
            clip_id
        )

        clip.track_id = (
            target_track.track_id
        )
        clip.start_time = float(
            new_start_time
        )
        clip.end_time = (
            clip.start_time
            + duration
        )

        target_track.clips.append(
            clip
        )
        target_track.sort_clips()

        return self._commit(
            operation_type=(
                TimelineEditingOperationType
                .MOVE_CLIP
            ),
            clip=clip,
            track=target_track,
            before=before,
            metadata={
                "source_track_id": (
                    source_track.track_id
                ),
                "target_track_id": (
                    target_track.track_id
                ),
            },
        )

    def trim_clip_start(
        self,
        clip_id: str,
        new_start_time: float,
    ) -> TimelineMutationResult:
        clip = self._timeline.get_clip(
            clip_id
        )
        track = (
            self._timeline.find_clip_track(
                clip_id
            )
        )

        if clip is None or track is None:
            return self._failure(
                f"Timeline clip does not exist: {clip_id}"
            )

        validation = (
            self.validator
            .validate_trim_start(
                timeline=self._timeline,
                clip_id=clip_id,
                new_start_time=(
                    new_start_time
                ),
            )
        )

        if not validation.valid:
            return self._validation_failure(
                validation
            )

        before = clip.to_dict()

        delta = (
            float(new_start_time)
            - clip.start_time
        )

        clip.start_time = float(
            new_start_time
        )

        if clip.source_start is not None:
            clip.source_start += delta

        track.sort_clips()

        return self._commit(
            operation_type=(
                TimelineEditingOperationType
                .TRIM_CLIP_START
            ),
            clip=clip,
            track=track,
            before=before,
            metadata={
                "trim_delta": delta,
            },
        )

    def trim_clip_end(
        self,
        clip_id: str,
        new_end_time: float,
    ) -> TimelineMutationResult:
        clip = self._timeline.get_clip(
            clip_id
        )
        track = (
            self._timeline.find_clip_track(
                clip_id
            )
        )

        if clip is None or track is None:
            return self._failure(
                f"Timeline clip does not exist: {clip_id}"
            )

        validation = (
            self.validator.validate_trim_end(
                timeline=self._timeline,
                clip_id=clip_id,
                new_end_time=new_end_time,
            )
        )

        if not validation.valid:
            return self._validation_failure(
                validation
            )

        before = clip.to_dict()

        delta = (
            clip.end_time
            - float(new_end_time)
        )

        clip.end_time = float(
            new_end_time
        )

        if clip.source_end is not None:
            clip.source_end -= delta

        track.sort_clips()

        return self._commit(
            operation_type=(
                TimelineEditingOperationType
                .TRIM_CLIP_END
            ),
            clip=clip,
            track=track,
            before=before,
            metadata={
                "trim_delta": delta,
            },
        )

    def insert_clip(
        self,
        track_id: str,
        clip: EditableTimelineClip,
    ) -> TimelineMutationResult:
        candidate = clip.clone()
        candidate.track_id = track_id

        validation = (
            self.validator.validate_insert(
                timeline=self._timeline,
                track_id=track_id,
                clip=candidate,
            )
        )

        if not validation.valid:
            return self._validation_failure(
                validation
            )

        track = self._timeline.get_track(
            track_id
        )

        if track is None:
            return self._failure(
                "Target track does not exist."
            )

        track.clips.append(candidate)
        track.sort_clips()

        return self._commit(
            operation_type=(
                TimelineEditingOperationType
                .INSERT_CLIP
            ),
            clip=candidate,
            track=track,
            before=None,
        )

    def split_clip(
        self,
        clip_id: str,
        split_time: float,
        *,
        right_clip_id: str | None = None,
    ) -> TimelineMutationResult:
        clip = self._timeline.get_clip(
            clip_id
        )
        track = (
            self._timeline.find_clip_track(
                clip_id
            )
        )

        if clip is None or track is None:
            return self._failure(
                f"Timeline clip does not exist: {clip_id}"
            )

        editable = (
            self.validator
            .validate_track_editable(track)
        )

        if not editable.valid:
            return self._validation_failure(
                editable
            )

        split_time = float(split_time)
        minimum = (
            self._timeline
            .minimum_clip_duration
        )

        if not (
            clip.start_time + minimum
            <= split_time
            <= clip.end_time - minimum
        ):
            return self._failure(
                "Split point must be inside the "
                "clip and leave at least one "
                "frame on each side."
            )

        before = clip.to_dict()
        left_duration = (
            split_time
            - clip.start_time
        )

        original_end = clip.end_time
        original_source_end = (
            clip.source_end
        )

        clip.end_time = split_time

        if clip.source_start is not None:
            clip.source_end = (
                clip.source_start
                + left_duration
            )

        right_clip = deepcopy(clip)

        right_clip.clip_id = (
            right_clip_id
            or f"{clip_id}_split_{uuid4().hex[:8]}"
        )

        right_clip.start_time = split_time
        right_clip.end_time = original_end

        if clip.source_end is not None:
            right_clip.source_start = (
                clip.source_end
            )
            right_clip.source_end = (
                original_source_end
            )

        validation = (
            self.validator.validate_insert(
                timeline=self._timeline,
                track_id=track.track_id,
                clip=right_clip,
            )
        )

        if not validation.valid:
            self._restore_clip(
                clip,
                before,
            )

            return self._validation_failure(
                validation
            )

        track.clips.append(right_clip)
        track.sort_clips()

        result = self._commit(
            operation_type=(
                TimelineEditingOperationType
                .SPLIT_CLIP
            ),
            clip=right_clip,
            track=track,
            before=before,
            metadata={
                "left_clip_id": clip.clip_id,
                "right_clip_id": (
                    right_clip.clip_id
                ),
                "split_time": split_time,
                "left_clip": clip.to_dict(),
                "right_clip": (
                    right_clip.to_dict()
                ),
            },
        )

        return result

    def duplicate_clip(
        self,
        clip_id: str,
        *,
        new_clip_id: str | None = None,
        new_start_time: float | None = None,
        target_track_id: str | None = None,
    ) -> TimelineMutationResult:
        source = self._timeline.get_clip(
            clip_id
        )

        source_track = (
            self._timeline.find_clip_track(
                clip_id
            )
        )

        if (
            source is None
            or source_track is None
        ):
            return self._failure(
                f"Timeline clip does not exist: {clip_id}"
            )

        target_track_id = (
            target_track_id
            or source_track.track_id
        )

        duplicate = source.clone()
        duplicate.clip_id = (
            new_clip_id
            or f"{clip_id}_copy_{uuid4().hex[:8]}"
        )
        duplicate.track_id = (
            target_track_id
        )

        start_time = (
            float(new_start_time)
            if new_start_time is not None
            else source.end_time
        )

        duplicate.start_time = start_time
        duplicate.end_time = (
            start_time
            + source.duration
        )

        validation = (
            self.validator.validate_insert(
                timeline=self._timeline,
                track_id=target_track_id,
                clip=duplicate,
            )
        )

        if not validation.valid:
            return self._validation_failure(
                validation
            )

        track = self._timeline.get_track(
            target_track_id
        )

        if track is None:
            return self._failure(
                "Target track does not exist."
            )

        track.clips.append(duplicate)
        track.sort_clips()

        return self._commit(
            operation_type=(
                TimelineEditingOperationType
                .DUPLICATE_CLIP
            ),
            clip=duplicate,
            track=track,
            before=source.to_dict(),
            metadata={
                "source_clip_id": clip_id,
            },
        )

    def delete_clip(
        self,
        clip_id: str,
        *,
        close_gap: bool = False,
    ) -> TimelineMutationResult:
        track = (
            self._timeline.find_clip_track(
                clip_id
            )
        )

        if track is None:
            return self._failure(
                f"Timeline clip does not exist: {clip_id}"
            )

        editable = (
            self.validator
            .validate_track_editable(track)
        )

        if not editable.valid:
            return self._validation_failure(
                editable
            )

        clip = track.get_clip(
            clip_id
        )

        if clip is None:
            return self._failure(
                f"Timeline clip does not exist: {clip_id}"
            )

        before = clip.to_dict()
        removed_start = clip.start_time
        removed_end = clip.end_time

        track.remove_clip(
            clip_id
        )

        if close_gap:
            gap_duration = (
                removed_end
                - removed_start
            )

            for item in track.clips:
                if (
                    item.start_time
                    >= removed_end
                ):
                    item.start_time -= (
                        gap_duration
                    )
                    item.end_time -= (
                        gap_duration
                    )

            track.sort_clips()

        return self._commit(
            operation_type=(
                TimelineEditingOperationType
                .DELETE_CLIP
            ),
            clip=None,
            track=track,
            before=before,
            metadata={
                "close_gap": close_gap,
                "removed_start": removed_start,
                "removed_end": removed_end,
            },
        )

    def close_gap(
        self,
        track_id: str,
        gap_start: float,
        gap_end: float,
    ) -> TimelineMutationResult:
        track = self._timeline.get_track(
            track_id
        )

        if track is None:
            return self._failure(
                f"Timeline track does not exist: {track_id}"
            )

        editable = (
            self.validator
            .validate_track_editable(track)
        )

        if not editable.valid:
            return self._validation_failure(
                editable
            )

        gap_start = float(gap_start)
        gap_end = float(gap_end)

        if gap_start < 0 or gap_end <= gap_start:
            return self._failure(
                "Gap range is invalid."
            )

        gap_duration = (
            gap_end - gap_start
        )

        before = track.to_dict()

        affected = [
            clip
            for clip in track.clips
            if clip.start_time >= gap_end
        ]

        if not affected:
            return self._failure(
                "No clips exist after the gap."
            )

        for clip in affected:
            clip.start_time -= gap_duration
            clip.end_time -= gap_duration

        track.sort_clips()

        validation = (
            self.validator.validate_timeline(
                self._timeline
            )
        )

        if not validation.valid:
            self._restore_track(
                track,
                before,
            )
            return self._validation_failure(
                validation
            )

        return self._commit(
            operation_type=(
                TimelineEditingOperationType
                .CLOSE_GAP
            ),
            clip=None,
            track=track,
            before=before,
            metadata={
                "gap_start": gap_start,
                "gap_end": gap_end,
                "gap_duration": gap_duration,
                "affected_clip_ids": [
                    clip.clip_id
                    for clip in affected
                ],
            },
        )

    def close_all_gaps(
        self,
        track_id: str,
    ) -> TimelineMutationResult:
        track = self._timeline.get_track(
            track_id
        )

        if track is None:
            return self._failure(
                f"Timeline track does not exist: {track_id}"
            )

        editable = (
            self.validator
            .validate_track_editable(track)
        )

        if not editable.valid:
            return self._validation_failure(
                editable
            )

        before = track.to_dict()
        track.sort_clips()

        cursor = 0.0
        gap_count = 0

        for clip in track.clips:
            if clip.start_time > cursor:
                duration = clip.duration

                clip.start_time = cursor
                clip.end_time = (
                    cursor + duration
                )

                gap_count += 1

            cursor = max(
                cursor,
                clip.end_time,
            )

        if gap_count == 0:
            return self._failure(
                "Track does not contain gaps."
            )

        return self._commit(
            operation_type=(
                TimelineEditingOperationType
                .CLOSE_GAP
            ),
            clip=None,
            track=track,
            before=before,
            metadata={
                "close_all": True,
                "gap_count": gap_count,
            },
        )

    def insert_clips(
            self,
            clips: list[EditableTimelineClip],
        ) -> TimelineMutationResult:
        if not clips:
            return self._failure(
                "Không có clip nào để thêm."
            )

        working_timeline = (
            self._timeline.clone()
        )

        inserted_clips: list[
            EditableTimelineClip
        ] = []

        affected_track_ids: list[str] = []

        for raw_clip in clips:
            candidate = raw_clip.clone()

            validation = (
                self.validator.validate_insert(
                    timeline=working_timeline,
                    track_id=candidate.track_id,
                    clip=candidate,
                )
            )

            if not validation.valid:
                return self._validation_failure(
                    validation
                )

            track = working_timeline.get_track(
                candidate.track_id
            )

            if track is None:
                return self._failure(
                    "Không tìm thấy track đích: "
                    f"{candidate.track_id}"
                )

            track.clips.append(candidate)
            track.sort_clips()

            inserted_clips.append(
                candidate
            )

            if (
                track.track_id
                not in affected_track_ids
            ):
                affected_track_ids.append(
                    track.track_id
                )

        before = self._timeline.to_dict()

        self._timeline = working_timeline

        for track_id in affected_track_ids:
            track = self._timeline.get_track(
                track_id
            )

            if track:
                track.sort_clips()

        self._timeline.recalculate_duration()
        self._timeline.mark_dirty()

        event = TimelineEditingEvent(
            operation_type=(
                TimelineEditingOperationType
                .PASTE_CLIPS
            ),
            production_id=(
                self._timeline.production_id
            ),
            revision=self._timeline.revision,
            clip_id=None,
            track_id=None,
            before=before,
            after=self._timeline.to_dict(),
            metadata={
                "inserted_clip_ids": [
                    clip.clip_id
                    for clip in inserted_clips
                ],
                "affected_track_ids": (
                    affected_track_ids
                ),
                "clip_count": len(
                    inserted_clips
                ),
            },
        )

        self._events.append(event)

        return TimelineMutationResult(
            success=True,
            timeline=self.timeline,
            event=event,
            validation=(
                TimelineEditingValidationResult(
                    valid=True
                )
            ),
            changed_clip=None,
            changed_track=None,
            metadata={
                "revision": (
                    self._timeline.revision
                ),
                "dirty": (
                    self._timeline.dirty
                ),
                "inserted_clip_ids": [
                    clip.clip_id
                    for clip in inserted_clips
                ],
            },
        )


    def delete_clips(
        self,
        clip_ids: list[str],
    ) -> TimelineMutationResult:
        normalized_ids = list(
            dict.fromkeys(
                str(clip_id).strip()
                for clip_id in clip_ids
                if str(clip_id).strip()
            )
        )

        if not normalized_ids:
            return self._failure(
                "Không có clip nào để xóa."
            )

        working_timeline = (
            self._timeline.clone()
        )

        missing_ids: list[str] = []
        locked_track_ids: list[str] = []

        for clip_id in normalized_ids:
            track = (
                working_timeline
                .find_clip_track(clip_id)
            )

            if track is None:
                missing_ids.append(clip_id)
                continue

            if track.locked:
                locked_track_ids.append(
                    track.track_id
                )

        if missing_ids:
            return self._failure(
                "Không tìm thấy clip: "
                + ", ".join(missing_ids)
            )

        if locked_track_ids:
            return self._failure(
                "Không thể cắt clip trên track "
                "đang khóa: "
                + ", ".join(
                    dict.fromkeys(
                        locked_track_ids
                    )
                )
            )

        before = self._timeline.to_dict()
        removed_payloads: list[
            dict[str, Any]
        ] = []

        affected_track_ids: list[str] = []

        for clip_id in normalized_ids:
            track = (
                working_timeline
                .find_clip_track(clip_id)
            )

            if track is None:
                continue

            clip = track.remove_clip(
                clip_id
            )

            if clip is None:
                continue

            removed_payloads.append(
                clip.to_dict()
            )

            if (
                track.track_id
                not in affected_track_ids
            ):
                affected_track_ids.append(
                    track.track_id
                )

        self._timeline = working_timeline
        self._timeline.recalculate_duration()
        self._timeline.mark_dirty()

        event = TimelineEditingEvent(
            operation_type=(
                TimelineEditingOperationType
                .CUT_CLIPS
            ),
            production_id=(
                self._timeline.production_id
            ),
            revision=self._timeline.revision,
            clip_id=None,
            track_id=None,
            before=before,
            after=self._timeline.to_dict(),
            metadata={
                "removed_clip_ids": (
                    normalized_ids
                ),
                "removed_clips": (
                    removed_payloads
                ),
                "affected_track_ids": (
                    affected_track_ids
                ),
                "clip_count": len(
                    removed_payloads
                ),
            },
        )

        self._events.append(event)

        return TimelineMutationResult(
            success=True,
            timeline=self.timeline,
            event=event,
            validation=(
                TimelineEditingValidationResult(
                    valid=True
                )
            ),
            metadata={
                "revision": (
                    self._timeline.revision
                ),
                "dirty": (
                    self._timeline.dirty
                ),
                "removed_clip_ids": (
                    normalized_ids
                ),
            },
        )

    def reset(
        self,
    ) -> EditableTimeline:
        self._timeline = (
            self._original_timeline.clone()
        )
        self._events.clear()

        return self.timeline

    def to_dict(self) -> dict[str, Any]:
        return {
            "timeline": (
                self._timeline.to_dict()
            ),
            "original_timeline": (
                self._original_timeline.to_dict()
            ),
            "events": [
                event.to_dict()
                for event in self._events
            ],
            "metadata": {
                "runtime": (
                    "TimelineMutationRuntime"
                ),
                "event_count": len(
                    self._events
                ),
            },
        }

    def _commit(
        self,
        *,
        operation_type: (
            TimelineEditingOperationType
        ),
        clip: EditableTimelineClip | None,
        track: EditableTimelineTrack,
        before: dict[str, Any] | None,
        metadata: dict[str, Any] | None = None,
    ) -> TimelineMutationResult:
        track.sort_clips()
        self._timeline.recalculate_duration()
        self._timeline.mark_dirty()

        after = (
            clip.to_dict()
            if clip is not None
            else track.to_dict()
        )

        event = TimelineEditingEvent(
            operation_type=operation_type,
            production_id=(
                self._timeline.production_id
            ),
            revision=(
                self._timeline.revision
            ),
            clip_id=(
                clip.clip_id
                if clip
                else None
            ),
            track_id=track.track_id,
            before=deepcopy(before),
            after=deepcopy(after),
            metadata=dict(
                metadata or {}
            ),
        )

        self._events.append(event)

        return TimelineMutationResult(
            success=True,
            timeline=self.timeline,
            event=event,
            validation=(
                TimelineEditingValidationResult(
                    valid=True
                )
            ),
            changed_clip=(
                clip.clone()
                if clip
                else None
            ),
            changed_track=track.clone(),
            error=None,
            metadata={
                "revision": (
                    self._timeline.revision
                ),
                "dirty": (
                    self._timeline.dirty
                ),
            },
        )

    def _validation_failure(
        self,
        validation: (
            TimelineEditingValidationResult
        ),
    ) -> TimelineMutationResult:
        message = "; ".join(
            issue.message
            for issue in validation.issues
        )

        return TimelineMutationResult(
            success=False,
            timeline=self.timeline,
            validation=validation,
            error=message,
        )

    def _failure(
        self,
        message: str,
    ) -> TimelineMutationResult:
        return TimelineMutationResult(
            success=False,
            timeline=self.timeline,
            error=message,
        )

    def _restore_clip(
        self,
        clip: EditableTimelineClip,
        payload: dict[str, Any],
    ) -> None:
        clip.start_time = float(
            payload["start_time"]
        )
        clip.end_time = float(
            payload["end_time"]
        )
        clip.source_start = payload.get(
            "source_start"
        )
        clip.source_end = payload.get(
            "source_end"
        )

    def _restore_track(
        self,
        track: EditableTimelineTrack,
        payload: dict[str, Any],
    ) -> None:
        restored = (
            EditableTimelineTrack(
                track_id=payload[
                    "track_id"
                ],
                track_type=payload[
                    "track_type"
                ],
                name=payload.get(
                    "name"
                ),
                position=payload.get(
                    "position",
                    0,
                ),
                layer=payload.get(
                    "layer",
                    0,
                ),
                locked=payload.get(
                    "locked",
                    False,
                ),
                muted=payload.get(
                    "muted",
                    False,
                ),
                hidden=payload.get(
                    "hidden",
                    False,
                ),
                enabled=payload.get(
                    "enabled",
                    True,
                ),
                overlap_policy=payload.get(
                    "overlap_policy",
                    "forbid",
                ),
                clips=[
                    EditableTimelineClip(
                        clip_id=item[
                            "clip_id"
                        ],
                        track_id=item[
                            "track_id"
                        ],
                        clip_type=item[
                            "clip_type"
                        ],
                        start_time=item[
                            "start_time"
                        ],
                        end_time=item[
                            "end_time"
                        ],
                        source_start=item.get(
                            "source_start"
                        ),
                        source_end=item.get(
                            "source_end"
                        ),
                        source_duration=item.get(
                            "source_duration"
                        ),
                        asset_id=item.get(
                            "asset_id"
                        ),
                        local_path=item.get(
                            "local_path"
                        ),
                        text=item.get(
                            "text"
                        ),
                        volume=item.get(
                            "volume"
                        ),
                        opacity=item.get(
                            "opacity"
                        ),
                        speed=item.get(
                            "speed"
                        ),
                        enabled=item.get(
                            "enabled",
                            True,
                        ),
                        metadata=item.get(
                            "metadata",
                            {},
                        ),
                    )
                    for item
                    in payload.get(
                        "clips",
                        [],
                    )
                ],
                metadata=payload.get(
                    "metadata",
                    {},
                ),
            )
        )

        track.__dict__.update(
            restored.__dict__
        )


def build_timeline_mutation_runtime(
    timeline: EditableTimeline,
    *,
    validator: TimelineEditingValidator | None = None,
) -> TimelineMutationRuntime:
    return TimelineMutationRuntime(
        timeline=timeline,
        validator=validator,
    )

def replace_timeline(
    self,
    timeline: EditableTimeline,
    *,
    clear_events: bool = False,
) -> EditableTimeline:
    self._timeline = timeline.clone()

    if clear_events:
        self._events.clear()

    return self.timeline

def snapshot(
    self,
) -> EditableTimeline:
    return self.timeline


def replace_timeline(
    self,
    timeline: EditableTimeline,
    *,
    clear_events: bool = False,
) -> EditableTimeline:
    self._timeline = timeline.clone()

    if clear_events:
        self._events.clear()

    return self.timeline