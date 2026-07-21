from __future__ import annotations

from copy import deepcopy
from threading import RLock
from typing import Iterable

from app.review.editing.models import EditableTimeline, EditableTimelineTrack
from app.review.editing.ripple.enums import RippleEditOperation, RippleEditPolicy
from app.review.editing.ripple.models import RippleEditRequest, RippleEditResult
from app.review.editing.state.store import TimelineRuntimeStore


_EPSILON = 1e-9


class RippleEditRuntime:
    """Atomic ripple editing over the backend-authoritative timeline store.

    MVP policy deliberately closes one deterministic time range. Clips that
    partially cross that range are rejected rather than silently trimmed.
    """

    def __init__(self, *, store: TimelineRuntimeStore):
        self.store = store
        self._lock = RLock()

    def execute(self, request: RippleEditRequest) -> RippleEditResult:
        with self._lock:
            timeline = self.store.snapshot()
            conflict = self._revision_conflict(timeline, request)
            if conflict:
                return self._failure(timeline, request, conflict)
            if request.policy is RippleEditPolicy.DISABLED:
                return self._failure(timeline, request, "Ripple editing is disabled.")
            if request.operation is RippleEditOperation.DELETE:
                return self._delete(timeline, request)
            if request.operation is RippleEditOperation.CLOSE_RANGE:
                return self._close_range(timeline, request)
            return self._failure(timeline, request, "Unsupported ripple operation.")

    def delete_clips(
        self,
        clip_ids: Iterable[str],
        *,
        policy: RippleEditPolicy = RippleEditPolicy.TRACK,
        anchor_track_id: str | None = None,
        expected_revision: int | None = None,
    ) -> RippleEditResult:
        return self.execute(RippleEditRequest(
            operation=RippleEditOperation.DELETE,
            policy=policy,
            clip_ids=tuple(clip_ids),
            anchor_track_id=anchor_track_id,
            expected_revision=expected_revision,
        ))

    def close_range(
        self,
        range_start: float,
        range_end: float,
        *,
        policy: RippleEditPolicy = RippleEditPolicy.TRACK,
        anchor_track_id: str | None = None,
        expected_revision: int | None = None,
    ) -> RippleEditResult:
        return self.execute(RippleEditRequest(
            operation=RippleEditOperation.CLOSE_RANGE,
            policy=policy,
            range_start=range_start,
            range_end=range_end,
            anchor_track_id=anchor_track_id,
            expected_revision=expected_revision,
        ))

    def _delete(self, timeline: EditableTimeline, request: RippleEditRequest) -> RippleEditResult:
        if not request.clip_ids:
            return self._failure(timeline, request, "At least one clip is required.")
        clips = []
        tracks = []
        for clip_id in request.clip_ids:
            clip = timeline.get_clip(clip_id)
            track = timeline.find_clip_track(clip_id)
            if clip is None or track is None:
                return self._failure(timeline, request, f"Timeline clip does not exist: {clip_id}")
            if track.locked:
                return self._failure(timeline, request, f"Track is locked: {track.track_id}")
            clips.append(clip)
            tracks.append(track)
        start = min(clip.start_time for clip in clips)
        end = max(clip.end_time for clip in clips)
        selected = set(request.clip_ids)
        affected = self._resolve_tracks(timeline, request, tracks)
        error = self._validate_range(affected, start, end, selected)
        if error:
            return self._failure(timeline, request, error)
        for track in tracks:
            for clip_id in request.clip_ids:
                track.remove_clip(clip_id)
        return self._commit(timeline, request, start, end, affected, selected)

    def _close_range(self, timeline: EditableTimeline, request: RippleEditRequest) -> RippleEditResult:
        if request.range_start is None or request.range_end is None:
            return self._failure(timeline, request, "Ripple range is required.")
        start, end = float(request.range_start), float(request.range_end)
        if start < 0 or end <= start:
            return self._failure(timeline, request, "Ripple range is invalid.")
        affected = self._resolve_tracks(timeline, request, [])
        error = self._validate_range(affected, start, end, set())
        if error:
            return self._failure(timeline, request, error)
        return self._commit(timeline, request, start, end, affected, set())

    def _resolve_tracks(self, timeline, request, source_tracks):
        if request.policy is RippleEditPolicy.ALL_UNLOCKED_TRACKS:
            return [track for track in timeline.tracks if not track.locked]
        track_id = request.anchor_track_id
        if track_id is None and source_tracks:
            unique = {track.track_id for track in source_tracks}
            if len(unique) != 1:
                return []
            track_id = next(iter(unique))
        track = timeline.get_track(track_id) if track_id else None
        return [track] if track is not None and not track.locked else []

    def _validate_range(self, tracks, start, end, selected):
        if not tracks:
            return "Ripple target track could not be resolved or is locked."
        for track in tracks:
            for clip in track.clips:
                if clip.clip_id in selected:
                    continue
                intersects = clip.start_time < end - _EPSILON and clip.end_time > start + _EPSILON
                if intersects:
                    return (
                        f"Clip {clip.clip_id} crosses ripple range on track "
                        f"{track.track_id}; split or select it first."
                    )
        return None

    def _commit(self, timeline, request, start, end, affected_tracks, selected):
        delta = end - start
        shifted = []
        affected_ids = []
        for track in affected_tracks:
            affected_ids.append(track.track_id)
            for clip in track.clips:
                if clip.clip_id in selected:
                    continue
                if clip.start_time >= end - _EPSILON:
                    clip.start_time = max(0.0, clip.start_time - delta)
                    clip.end_time = max(clip.start_time, clip.end_time - delta)
                    shifted.append(clip.clip_id)
            track.sort_clips()
        timeline.recalculate_duration()
        timeline.mark_dirty()
        store_result = self.store.commit(
            timeline,
            reason=f"ripple.{request.operation.value}",
            metadata={
                "operation": request.operation.value,
                "policy": request.policy.value,
                "ripple_start": start,
                "ripple_end": end,
                "ripple_delta": delta,
                "removed_clip_ids": list(selected),
                "shifted_clip_ids": shifted,
                "affected_track_ids": affected_ids,
            },
        )
        if not store_result.success:
            return self._failure(self.store.snapshot(), request, store_result.error or "Ripple commit failed.")
        return RippleEditResult(
            success=True,
            timeline=store_result.timeline,
            operation=request.operation,
            policy=request.policy,
            removed_clip_ids=tuple(request.clip_ids),
            shifted_clip_ids=tuple(shifted),
            affected_track_ids=tuple(affected_ids),
            ripple_start=start,
            ripple_end=end,
            ripple_delta=delta,
            metadata={"atomic_commit": True, "commit_count": 1},
        )

    @staticmethod
    def _revision_conflict(timeline, request):
        if request.expected_revision is None:
            return None
        if int(request.expected_revision) != int(timeline.revision):
            return (
                "Timeline revision conflict: expected "
                f"{request.expected_revision}, current {timeline.revision}."
            )
        return None

    @staticmethod
    def _failure(timeline, request, error):
        return RippleEditResult(
            success=False,
            timeline=timeline.clone(),
            operation=request.operation,
            policy=request.policy,
            error=error,
            metadata={"atomic_commit": False, "commit_count": 0},
        )
