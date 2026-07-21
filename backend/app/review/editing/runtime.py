from __future__ import annotations

from copy import deepcopy
from typing import Any
from uuid import uuid4

from app.review.editing.enums import TimelineEditingOperationType
from app.review.editing.models import (
    EditableTimeline,
    EditableTimelineClip,
    EditableTimelineTrack,
    TimelineEditingEvent,
    TimelineEditingValidationResult,
    TimelineMutationResult,
)
from app.review.editing.state.store import TimelineRuntimeStore
from app.review.editing.validator import TimelineEditingValidator


class TimelineMutationRuntime:
    def __init__(
        self,
        timeline: EditableTimeline | None = None,
        *,
        store: TimelineRuntimeStore | None = None,
        validator: TimelineEditingValidator | None = None,
    ):
        if timeline is None and store is None:
            raise ValueError("Timeline or runtime store is required.")

        if timeline is not None and store is not None:
            raise ValueError(
                "Provide either timeline or runtime store, not both."
            )

        self.store = store or TimelineRuntimeStore(timeline=timeline)
        self.validator = validator or TimelineEditingValidator()
        self._events: list[TimelineEditingEvent] = []

    @property
    def timeline(self) -> EditableTimeline:
        return self.store.snapshot()

    @property
    def original_timeline(self) -> EditableTimeline:
        return self.store.initial_snapshot()

    @property
    def events(self) -> list[TimelineEditingEvent]:
        return list(self._events)

    def snapshot(self) -> EditableTimeline:
        return self.store.snapshot()

    def replace_timeline(
        self,
        timeline: EditableTimeline,
        *,
        clear_events: bool = False,
    ) -> EditableTimeline:
        result = self.store.replace(
            timeline,
            reason="mutation_runtime.replace_timeline",
            metadata={"clear_events": clear_events},
        )

        if result.success and clear_events:
            self._events.clear()

        return result.timeline

    def move_clip(
        self,
        clip_id: str,
        new_start_time: float,
        *,
        target_track_id: str | None = None,
    ) -> TimelineMutationResult:
        timeline = self.store.snapshot()
        clip = timeline.get_clip(clip_id)
        source_track = timeline.find_clip_track(clip_id)

        if clip is None or source_track is None:
            return self._failure(
                f"Timeline clip does not exist: {clip_id}"
            )

        resolved_track_id = target_track_id or source_track.track_id
        validation = self.validator.validate_move(
            timeline=timeline,
            clip_id=clip_id,
            target_track_id=resolved_track_id,
            new_start_time=new_start_time,
        )

        if not validation.valid:
            return self._validation_failure(validation)

        target_track = timeline.get_track(resolved_track_id)
        if target_track is None:
            return self._failure("Target track does not exist.")

        before = clip.to_dict()
        duration = clip.duration
        source_track.remove_clip(clip_id)

        clip.track_id = target_track.track_id
        clip.start_time = float(new_start_time)
        clip.end_time = clip.start_time + duration

        target_track.clips.append(clip)
        target_track.sort_clips()

        return self._commit(
            timeline=timeline,
            operation_type=TimelineEditingOperationType.MOVE_CLIP,
            clip=clip,
            track=target_track,
            before=before,
            metadata={
                "source_track_id": source_track.track_id,
                "target_track_id": target_track.track_id,
            },
        )

    def trim_clip_start(
        self,
        clip_id: str,
        new_start_time: float,
    ) -> TimelineMutationResult:
        timeline = self.store.snapshot()
        clip = timeline.get_clip(clip_id)
        track = timeline.find_clip_track(clip_id)

        if clip is None or track is None:
            return self._failure(
                f"Timeline clip does not exist: {clip_id}"
            )

        validation = self.validator.validate_trim_start(
            timeline=timeline,
            clip_id=clip_id,
            new_start_time=new_start_time,
        )

        if not validation.valid:
            return self._validation_failure(validation)

        before = clip.to_dict()
        delta = float(new_start_time) - clip.start_time
        clip.start_time = float(new_start_time)

        if clip.source_start is not None:
            clip.source_start += delta

        track.sort_clips()

        return self._commit(
            timeline=timeline,
            operation_type=TimelineEditingOperationType.TRIM_CLIP_START,
            clip=clip,
            track=track,
            before=before,
            metadata={"trim_delta": delta},
        )

    def trim_clip_end(
        self,
        clip_id: str,
        new_end_time: float,
    ) -> TimelineMutationResult:
        timeline = self.store.snapshot()
        clip = timeline.get_clip(clip_id)
        track = timeline.find_clip_track(clip_id)

        if clip is None or track is None:
            return self._failure(
                f"Timeline clip does not exist: {clip_id}"
            )

        validation = self.validator.validate_trim_end(
            timeline=timeline,
            clip_id=clip_id,
            new_end_time=new_end_time,
        )

        if not validation.valid:
            return self._validation_failure(validation)

        before = clip.to_dict()
        delta = clip.end_time - float(new_end_time)
        clip.end_time = float(new_end_time)

        if clip.source_end is not None:
            clip.source_end -= delta

        track.sort_clips()

        return self._commit(
            timeline=timeline,
            operation_type=TimelineEditingOperationType.TRIM_CLIP_END,
            clip=clip,
            track=track,
            before=before,
            metadata={"trim_delta": delta},
        )

    def insert_clip(
        self,
        track_id: str,
        clip: EditableTimelineClip,
    ) -> TimelineMutationResult:
        timeline = self.store.snapshot()
        candidate = clip.clone()
        candidate.track_id = track_id

        validation = self.validator.validate_insert(
            timeline=timeline,
            track_id=track_id,
            clip=candidate,
        )

        if not validation.valid:
            return self._validation_failure(validation)

        track = timeline.get_track(track_id)
        if track is None:
            return self._failure("Target track does not exist.")

        track.clips.append(candidate)
        track.sort_clips()

        return self._commit(
            timeline=timeline,
            operation_type=TimelineEditingOperationType.INSERT_CLIP,
            clip=candidate,
            track=track,
            before=None,
        )

    def insert_clips(
        self,
        clips: list[EditableTimelineClip],
    ) -> TimelineMutationResult:
        if not clips:
            return self._failure("Không có clip nào để thêm.")

        timeline = self.store.snapshot()
        before = timeline.to_dict()
        inserted_clips: list[EditableTimelineClip] = []
        affected_track_ids: list[str] = []

        for raw_clip in clips:
            candidate = raw_clip.clone()
            validation = self.validator.validate_insert(
                timeline=timeline,
                track_id=candidate.track_id,
                clip=candidate,
            )

            if not validation.valid:
                return self._validation_failure(validation)

            track = timeline.get_track(candidate.track_id)
            if track is None:
                return self._failure(
                    "Không tìm thấy track đích: "
                    f"{candidate.track_id}"
                )

            track.clips.append(candidate)
            track.sort_clips()
            inserted_clips.append(candidate)

            if track.track_id not in affected_track_ids:
                affected_track_ids.append(track.track_id)

        for track_id in affected_track_ids:
            track = timeline.get_track(track_id)
            if track is not None:
                track.sort_clips()

        inserted_clip_ids = [clip.clip_id for clip in inserted_clips]

        return self._commit_batch(
            timeline=timeline,
            operation_type=TimelineEditingOperationType.PASTE_CLIPS,
            before=before,
            metadata={
                "inserted_clip_ids": inserted_clip_ids,
                "affected_track_ids": affected_track_ids,
                "clip_count": len(inserted_clips),
            },
            result_metadata={"inserted_clip_ids": inserted_clip_ids},
        )

    def split_clip(
        self,
        clip_id: str,
        split_time: float,
        *,
        right_clip_id: str | None = None,
    ) -> TimelineMutationResult:
        timeline = self.store.snapshot()
        clip = timeline.get_clip(clip_id)
        track = timeline.find_clip_track(clip_id)

        if clip is None or track is None:
            return self._failure(
                f"Timeline clip does not exist: {clip_id}"
            )

        editable = self.validator.validate_track_editable(track)
        if not editable.valid:
            return self._validation_failure(editable)

        resolved_split_time = float(split_time)
        minimum = timeline.minimum_clip_duration

        if not (
            clip.start_time + minimum
            <= resolved_split_time
            <= clip.end_time - minimum
        ):
            return self._failure(
                "Split point must be inside the clip and leave at least "
                "one frame on each side."
            )

        before = clip.to_dict()
        left_duration = resolved_split_time - clip.start_time
        original_end = clip.end_time
        original_source_end = clip.source_end

        clip.end_time = resolved_split_time
        if clip.source_start is not None:
            clip.source_end = clip.source_start + left_duration

        right_clip = deepcopy(clip)
        right_clip.clip_id = (
            right_clip_id or f"{clip_id}_split_{uuid4().hex[:8]}"
        )
        right_clip.start_time = resolved_split_time
        right_clip.end_time = original_end

        if clip.source_end is not None:
            right_clip.source_start = clip.source_end
            right_clip.source_end = original_source_end

        validation = self.validator.validate_insert(
            timeline=timeline,
            track_id=track.track_id,
            clip=right_clip,
        )

        if not validation.valid:
            return self._validation_failure(validation)

        track.clips.append(right_clip)
        track.sort_clips()

        return self._commit(
            timeline=timeline,
            operation_type=TimelineEditingOperationType.SPLIT_CLIP,
            clip=right_clip,
            track=track,
            before=before,
            metadata={
                "left_clip_id": clip.clip_id,
                "right_clip_id": right_clip.clip_id,
                "split_time": resolved_split_time,
                "left_clip": clip.to_dict(),
                "right_clip": right_clip.to_dict(),
            },
        )

    def duplicate_clip(
        self,
        clip_id: str,
        *,
        new_clip_id: str | None = None,
        new_start_time: float | None = None,
        target_track_id: str | None = None,
    ) -> TimelineMutationResult:
        timeline = self.store.snapshot()
        source = timeline.get_clip(clip_id)
        source_track = timeline.find_clip_track(clip_id)

        if source is None or source_track is None:
            return self._failure(
                f"Timeline clip does not exist: {clip_id}"
            )

        resolved_track_id = target_track_id or source_track.track_id
        duplicate = source.clone()
        duplicate.clip_id = (
            new_clip_id or f"{clip_id}_copy_{uuid4().hex[:8]}"
        )
        duplicate.track_id = resolved_track_id
        start_time = (
            float(new_start_time)
            if new_start_time is not None
            else source.end_time
        )
        duplicate.start_time = start_time
        duplicate.end_time = start_time + source.duration

        validation = self.validator.validate_insert(
            timeline=timeline,
            track_id=resolved_track_id,
            clip=duplicate,
        )

        if not validation.valid:
            return self._validation_failure(validation)

        track = timeline.get_track(resolved_track_id)
        if track is None:
            return self._failure("Target track does not exist.")

        track.clips.append(duplicate)
        track.sort_clips()

        return self._commit(
            timeline=timeline,
            operation_type=TimelineEditingOperationType.DUPLICATE_CLIP,
            clip=duplicate,
            track=track,
            before=source.to_dict(),
            metadata={"source_clip_id": clip_id},
        )

    def delete_clip(
        self,
        clip_id: str,
        *,
        close_gap: bool = False,
    ) -> TimelineMutationResult:
        timeline = self.store.snapshot()
        track = timeline.find_clip_track(clip_id)

        if track is None:
            return self._failure(
                f"Timeline clip does not exist: {clip_id}"
            )

        editable = self.validator.validate_track_editable(track)
        if not editable.valid:
            return self._validation_failure(editable)

        clip = track.get_clip(clip_id)
        if clip is None:
            return self._failure(
                f"Timeline clip does not exist: {clip_id}"
            )

        before = clip.to_dict()
        removed_start = clip.start_time
        removed_end = clip.end_time
        track.remove_clip(clip_id)

        if close_gap:
            gap_duration = removed_end - removed_start
            for item in track.clips:
                if item.start_time >= removed_end:
                    item.start_time -= gap_duration
                    item.end_time -= gap_duration
            track.sort_clips()

        return self._commit(
            timeline=timeline,
            operation_type=TimelineEditingOperationType.DELETE_CLIP,
            clip=None,
            track=track,
            before=before,
            metadata={
                "close_gap": close_gap,
                "removed_start": removed_start,
                "removed_end": removed_end,
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
            return self._failure("Không có clip nào để xóa.")

        timeline = self.store.snapshot()
        missing_ids: list[str] = []
        locked_track_ids: list[str] = []

        for clip_id in normalized_ids:
            track = timeline.find_clip_track(clip_id)
            if track is None:
                missing_ids.append(clip_id)
            elif track.locked:
                locked_track_ids.append(track.track_id)

        if missing_ids:
            return self._failure(
                "Không tìm thấy clip: " + ", ".join(missing_ids)
            )

        if locked_track_ids:
            return self._failure(
                "Không thể cắt clip trên track đang khóa: "
                + ", ".join(dict.fromkeys(locked_track_ids))
            )

        before = timeline.to_dict()
        removed_payloads: list[dict[str, Any]] = []
        affected_track_ids: list[str] = []

        for clip_id in normalized_ids:
            track = timeline.find_clip_track(clip_id)
            if track is None:
                continue

            clip = track.remove_clip(clip_id)
            if clip is None:
                continue

            removed_payloads.append(clip.to_dict())
            if track.track_id not in affected_track_ids:
                affected_track_ids.append(track.track_id)

        return self._commit_batch(
            timeline=timeline,
            operation_type=TimelineEditingOperationType.CUT_CLIPS,
            before=before,
            metadata={
                "removed_clip_ids": normalized_ids,
                "removed_clips": removed_payloads,
                "affected_track_ids": affected_track_ids,
                "clip_count": len(removed_payloads),
            },
            result_metadata={"removed_clip_ids": normalized_ids},
        )

    def move_clips(
        self,
        clip_ids: list[str],
        delta_time: float,
    ) -> TimelineMutationResult:
        normalized_ids = self._normalize_clip_ids(
            clip_ids
        )
        if not normalized_ids:
            return self._failure(
                "Không có clip nào để di chuyển."
            )

        resolved_delta = float(delta_time)
        if resolved_delta == 0:
            return self._failure(
                "delta_time phải khác 0."
            )

        timeline = self.store.snapshot()
        selected: list[
            tuple[EditableTimelineClip, str]
        ] = []

        for clip_id in normalized_ids:
            clip = timeline.get_clip(clip_id)
            track = timeline.find_clip_track(clip_id)
            if clip is None or track is None:
                return self._failure(
                    "Không tìm thấy clip: " + clip_id
                )
            if track.locked:
                return self._failure(
                    "Không thể di chuyển clip trên "
                    "track đang khóa: " + track.track_id
                )
            selected.append((clip, track.track_id))

        before = timeline.to_dict()
        selected.sort(
            key=lambda item: (
                item[0].start_time,
                item[0].clip_id,
            )
        )

        for clip, track_id in selected:
            track = timeline.get_track(track_id)
            if track is not None:
                track.remove_clip(clip.clip_id)

        affected_track_ids: list[str] = []
        moved_ranges: list[dict[str, Any]] = []

        for clip, track_id in selected:
            new_start = clip.start_time + resolved_delta
            new_end = clip.end_time + resolved_delta
            if new_start < 0:
                return self._failure(
                    "Di chuyển nhiều clip vượt quá đầu timeline."
                )
            clip.start_time = new_start
            clip.end_time = new_end
            track = timeline.get_track(track_id)
            if track is None:
                return self._failure(
                    "Không tìm thấy track: " + track_id
                )
            track.clips.append(clip)
            track.sort_clips()
            if track_id not in affected_track_ids:
                affected_track_ids.append(track_id)
            moved_ranges.append({
                "clip_id": clip.clip_id,
                "track_id": track_id,
                "start_time": clip.start_time,
                "end_time": clip.end_time,
            })

        validation = self.validator.validate_timeline(
            timeline
        )
        if not validation.valid:
            return self._validation_failure(validation)

        return self._commit_batch(
            timeline=timeline,
            operation_type=(
                TimelineEditingOperationType.MOVE_CLIPS
            ),
            before=before,
            metadata={
                "clip_ids": normalized_ids,
                "delta_time": resolved_delta,
                "affected_track_ids": affected_track_ids,
                "moved_ranges": moved_ranges,
                "clip_count": len(selected),
            },
            result_metadata={
                "clip_ids": normalized_ids,
                "delta_time": resolved_delta,
            },
        )

    def duplicate_clips(
        self,
        clip_ids: list[str],
        *,
        time_offset: float | None = None,
    ) -> TimelineMutationResult:
        normalized_ids = self._normalize_clip_ids(
            clip_ids
        )
        if not normalized_ids:
            return self._failure(
                "Không có clip nào để nhân bản."
            )

        timeline = self.store.snapshot()
        selected: list[
            tuple[EditableTimelineClip, str]
        ] = []

        for clip_id in normalized_ids:
            clip = timeline.get_clip(clip_id)
            track = timeline.find_clip_track(clip_id)
            if clip is None or track is None:
                return self._failure(
                    "Không tìm thấy clip: " + clip_id
                )
            if track.locked:
                return self._failure(
                    "Không thể nhân bản clip trên "
                    "track đang khóa: " + track.track_id
                )
            selected.append((clip, track.track_id))

        selected.sort(
            key=lambda item: (
                item[0].start_time,
                item[0].clip_id,
            )
        )
        group_start = min(
            clip.start_time for clip, _ in selected
        )
        group_end = max(
            clip.end_time for clip, _ in selected
        )
        resolved_offset = (
            float(time_offset)
            if time_offset is not None
            else group_end - group_start
        )
        if resolved_offset <= 0:
            return self._failure(
                "time_offset phải lớn hơn 0."
            )

        before = timeline.to_dict()
        duplicated_ids: list[str] = []
        affected_track_ids: list[str] = []

        for source, track_id in selected:
            duplicate = source.clone()
            duplicate.clip_id = (
                f"{source.clip_id}_copy_"
                f"{uuid4().hex[:8]}"
            )
            duplicate.start_time += resolved_offset
            duplicate.end_time += resolved_offset
            track = timeline.get_track(track_id)
            if track is None:
                return self._failure(
                    "Không tìm thấy track: " + track_id
                )
            track.clips.append(duplicate)
            track.sort_clips()
            duplicated_ids.append(duplicate.clip_id)
            if track_id not in affected_track_ids:
                affected_track_ids.append(track_id)

        validation = self.validator.validate_timeline(
            timeline
        )
        if not validation.valid:
            return self._validation_failure(validation)

        return self._commit_batch(
            timeline=timeline,
            operation_type=(
                TimelineEditingOperationType.DUPLICATE_CLIPS
            ),
            before=before,
            metadata={
                "source_clip_ids": normalized_ids,
                "duplicated_clip_ids": duplicated_ids,
                "time_offset": resolved_offset,
                "affected_track_ids": affected_track_ids,
                "clip_count": len(duplicated_ids),
            },
            result_metadata={
                "source_clip_ids": normalized_ids,
                "duplicated_clip_ids": duplicated_ids,
                "time_offset": resolved_offset,
            },
        )

    def delete_selected_clips(
        self,
        clip_ids: list[str],
    ) -> TimelineMutationResult:
        normalized_ids = self._normalize_clip_ids(
            clip_ids
        )
        if not normalized_ids:
            return self._failure(
                "Không có clip nào để xóa."
            )

        timeline = self.store.snapshot()
        before = timeline.to_dict()
        affected_track_ids: list[str] = []

        for clip_id in normalized_ids:
            track = timeline.find_clip_track(clip_id)
            if track is None:
                return self._failure(
                    "Không tìm thấy clip: " + clip_id
                )
            if track.locked:
                return self._failure(
                    "Không thể xóa clip trên track "
                    "đang khóa: " + track.track_id
                )

        for clip_id in normalized_ids:
            track = timeline.find_clip_track(clip_id)
            if track is None:
                continue
            track.remove_clip(clip_id)
            if track.track_id not in affected_track_ids:
                affected_track_ids.append(track.track_id)

        return self._commit_batch(
            timeline=timeline,
            operation_type=(
                TimelineEditingOperationType.DELETE_CLIPS
            ),
            before=before,
            metadata={
                "deleted_clip_ids": normalized_ids,
                "affected_track_ids": affected_track_ids,
                "clip_count": len(normalized_ids),
            },
            result_metadata={
                "deleted_clip_ids": normalized_ids,
            },
        )

    def close_gap(
        self,
        track_id: str,
        gap_start: float,
        gap_end: float,
    ) -> TimelineMutationResult:
        timeline = self.store.snapshot()
        track = timeline.get_track(track_id)

        if track is None:
            return self._failure(
                f"Timeline track does not exist: {track_id}"
            )

        editable = self.validator.validate_track_editable(track)
        if not editable.valid:
            return self._validation_failure(editable)

        resolved_gap_start = float(gap_start)
        resolved_gap_end = float(gap_end)

        if resolved_gap_start < 0 or resolved_gap_end <= resolved_gap_start:
            return self._failure("Gap range is invalid.")

        gap_duration = resolved_gap_end - resolved_gap_start
        before = track.to_dict()
        affected = [
            clip
            for clip in track.clips
            if clip.start_time >= resolved_gap_end
        ]

        if not affected:
            return self._failure("No clips exist after the gap.")

        for clip in affected:
            clip.start_time -= gap_duration
            clip.end_time -= gap_duration

        track.sort_clips()
        validation = self.validator.validate_timeline(timeline)
        if not validation.valid:
            return self._validation_failure(validation)

        return self._commit(
            timeline=timeline,
            operation_type=TimelineEditingOperationType.CLOSE_GAP,
            clip=None,
            track=track,
            before=before,
            metadata={
                "gap_start": resolved_gap_start,
                "gap_end": resolved_gap_end,
                "gap_duration": gap_duration,
                "affected_clip_ids": [clip.clip_id for clip in affected],
            },
        )

    def close_all_gaps(
        self,
        track_id: str,
    ) -> TimelineMutationResult:
        timeline = self.store.snapshot()
        track = timeline.get_track(track_id)

        if track is None:
            return self._failure(
                f"Timeline track does not exist: {track_id}"
            )

        editable = self.validator.validate_track_editable(track)
        if not editable.valid:
            return self._validation_failure(editable)

        before = track.to_dict()
        track.sort_clips()
        cursor = 0.0
        gap_count = 0

        for clip in track.clips:
            if clip.start_time > cursor:
                duration = clip.duration
                clip.start_time = cursor
                clip.end_time = cursor + duration
                gap_count += 1
            cursor = max(cursor, clip.end_time)

        if gap_count == 0:
            return self._failure("Track does not contain gaps.")

        return self._commit(
            timeline=timeline,
            operation_type=TimelineEditingOperationType.CLOSE_GAP,
            clip=None,
            track=track,
            before=before,
            metadata={"close_all": True, "gap_count": gap_count},
        )

    def reset(self) -> EditableTimeline:
        result = self.store.reset()
        if result.success:
            self._events.clear()
        return result.timeline

    def to_dict(self) -> dict[str, Any]:
        return {
            "timeline": self.timeline.to_dict(),
            "original_timeline": self.original_timeline.to_dict(),
            "events": [event.to_dict() for event in self._events],
            "metadata": {
                "runtime": "TimelineMutationRuntime",
                "event_count": len(self._events),
            },
        }

    def _commit(
        self,
        *,
        timeline: EditableTimeline,
        operation_type: TimelineEditingOperationType,
        clip: EditableTimelineClip | None,
        track: EditableTimelineTrack,
        before: dict[str, Any] | None,
        metadata: dict[str, Any] | None = None,
    ) -> TimelineMutationResult:
        track.sort_clips()
        timeline.recalculate_duration()
        timeline.mark_dirty()

        after = clip.to_dict() if clip is not None else track.to_dict()
        event = TimelineEditingEvent(
            operation_type=operation_type,
            production_id=timeline.production_id,
            revision=timeline.revision,
            clip_id=clip.clip_id if clip else None,
            track_id=track.track_id,
            before=deepcopy(before),
            after=deepcopy(after),
            metadata=dict(metadata or {}),
        )

        store_result = self.store.commit(
            timeline,
            reason=f"mutation.{operation_type.value}",
            metadata={
                "operation_type": operation_type.value,
                "clip_id": event.clip_id,
                "track_id": event.track_id,
            },
        )

        if not store_result.success:
            return self._failure(
                store_result.error or "Timeline store commit failed."
            )

        self._events.append(event)

        return TimelineMutationResult(
            success=True,
            timeline=store_result.timeline,
            event=event,
            validation=TimelineEditingValidationResult(valid=True),
            changed_clip=clip.clone() if clip else None,
            changed_track=track.clone(),
            error=None,
            metadata={
                "revision": store_result.timeline.revision,
                "dirty": store_result.timeline.dirty,
            },
        )

    def _commit_batch(
        self,
        *,
        timeline: EditableTimeline,
        operation_type: TimelineEditingOperationType,
        before: dict[str, Any],
        metadata: dict[str, Any],
        result_metadata: dict[str, Any],
    ) -> TimelineMutationResult:
        timeline.recalculate_duration()
        timeline.mark_dirty()

        event = TimelineEditingEvent(
            operation_type=operation_type,
            production_id=timeline.production_id,
            revision=timeline.revision,
            clip_id=None,
            track_id=None,
            before=deepcopy(before),
            after=timeline.to_dict(),
            metadata=deepcopy(metadata),
        )

        store_result = self.store.commit(
            timeline,
            reason=f"mutation.{operation_type.value}",
            metadata={
                "operation_type": operation_type.value,
                **deepcopy(metadata),
            },
        )

        if not store_result.success:
            return self._failure(
                store_result.error or "Timeline store commit failed."
            )

        self._events.append(event)

        return TimelineMutationResult(
            success=True,
            timeline=store_result.timeline,
            event=event,
            validation=TimelineEditingValidationResult(valid=True),
            changed_clip=None,
            changed_track=None,
            metadata={
                "revision": store_result.timeline.revision,
                "dirty": store_result.timeline.dirty,
                **deepcopy(result_metadata),
            },
        )

    def _validation_failure(
        self,
        validation: TimelineEditingValidationResult,
    ) -> TimelineMutationResult:
        message = "; ".join(issue.message for issue in validation.issues)
        return TimelineMutationResult(
            success=False,
            timeline=self.store.snapshot(),
            validation=validation,
            error=message,
        )

    @staticmethod
    def _normalize_clip_ids(
        clip_ids: list[str],
    ) -> list[str]:
        return list(
            dict.fromkeys(
                str(clip_id).strip()
                for clip_id in clip_ids
                if str(clip_id).strip()
            )
        )

    def _failure(self, message: str) -> TimelineMutationResult:
        return TimelineMutationResult(
            success=False,
            timeline=self.store.snapshot(),
            error=message,
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


def build_mutation_runtime_from_store(
    store: TimelineRuntimeStore,
    *,
    validator: TimelineEditingValidator | None = None,
) -> TimelineMutationRuntime:
    return TimelineMutationRuntime(
        store=store,
        validator=validator,
    )
