from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.review.editing.enums import (
    EditableClipType,
    EditableTrackType,
    TimelineDirtyStatus,
    TimelineEditingIssueCode,
    TimelineEditingOperationType,
    TimelineOverlapPolicy,
)


def utc_now_iso() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


@dataclass
class EditableTimelineClip:
    clip_id: str
    track_id: str
    clip_type: EditableClipType

    start_time: float
    end_time: float

    source_start: float | None = None
    source_end: float | None = None
    source_duration: float | None = None

    asset_id: str | None = None
    local_path: str | None = None

    text: str | None = None

    volume: float | None = None
    opacity: float | None = None
    speed: float | None = None

    enabled: bool = True

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        self.clip_id = str(
            self.clip_id
        ).strip()

        self.track_id = str(
            self.track_id
        ).strip()

        if not isinstance(
            self.clip_type,
            EditableClipType,
        ):
            try:
                self.clip_type = (
                    EditableClipType(
                        str(self.clip_type)
                    )
                )
            except ValueError:
                self.clip_type = (
                    EditableClipType.UNKNOWN
                )

        self.start_time = float(
            self.start_time
        )
        self.end_time = float(
            self.end_time
        )

        if self.source_start is not None:
            self.source_start = float(
                self.source_start
            )

        if self.source_end is not None:
            self.source_end = float(
                self.source_end
            )

        if self.source_duration is not None:
            self.source_duration = float(
                self.source_duration
            )

    @property
    def duration(self) -> float:
        return max(
            0.0,
            self.end_time
            - self.start_time,
        )

    @property
    def source_range_duration(
        self,
    ) -> float | None:
        if (
            self.source_start is None
            or self.source_end is None
        ):
            return None

        return max(
            0.0,
            self.source_end
            - self.source_start,
        )

    def clone(
        self,
    ) -> EditableTimelineClip:
        return deepcopy(self)

    def to_dict(self) -> dict[str, Any]:
        return {
            "clip_id": self.clip_id,
            "track_id": self.track_id,
            "clip_type": (
                self.clip_type.value
            ),
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "source_start": (
                self.source_start
            ),
            "source_end": self.source_end,
            "source_duration": (
                self.source_duration
            ),
            "source_range_duration": (
                self.source_range_duration
            ),
            "asset_id": self.asset_id,
            "local_path": self.local_path,
            "text": self.text,
            "volume": self.volume,
            "opacity": self.opacity,
            "speed": self.speed,
            "enabled": self.enabled,
            "metadata": deepcopy(
                self.metadata
            ),
        }


@dataclass
class EditableTimelineTrack:
    track_id: str
    track_type: EditableTrackType

    name: str | None = None
    position: int = 0
    layer: int = 0

    locked: bool = False
    muted: bool = False
    hidden: bool = False
    enabled: bool = True

    overlap_policy: TimelineOverlapPolicy = (
        TimelineOverlapPolicy.FORBID
    )

    clips: list[
        EditableTimelineClip
    ] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        self.track_id = str(
            self.track_id
        ).strip()

        if not isinstance(
            self.track_type,
            EditableTrackType,
        ):
            try:
                self.track_type = (
                    EditableTrackType(
                        str(self.track_type)
                    )
                )
            except ValueError:
                self.track_type = (
                    EditableTrackType.UNKNOWN
                )

        if not isinstance(
            self.overlap_policy,
            TimelineOverlapPolicy,
        ):
            self.overlap_policy = (
                TimelineOverlapPolicy(
                    str(
                        self.overlap_policy
                    )
                )
            )

        for clip in self.clips:
            clip.track_id = self.track_id

        self.sort_clips()

    def sort_clips(self) -> None:
        self.clips.sort(
            key=lambda item: (
                item.start_time,
                item.end_time,
                item.clip_id,
            )
        )

    def get_clip(
        self,
        clip_id: str,
    ) -> EditableTimelineClip | None:
        normalized_id = str(
            clip_id
        )

        return next(
            (
                clip
                for clip in self.clips
                if clip.clip_id
                == normalized_id
            ),
            None,
        )

    def remove_clip(
        self,
        clip_id: str,
    ) -> EditableTimelineClip | None:
        clip = self.get_clip(
            clip_id
        )

        if clip is None:
            return None

        self.clips.remove(clip)
        return clip

    def clone(
        self,
    ) -> EditableTimelineTrack:
        return deepcopy(self)

    def to_dict(self) -> dict[str, Any]:
        return {
            "track_id": self.track_id,
            "track_type": (
                self.track_type.value
            ),
            "name": self.name,
            "position": self.position,
            "layer": self.layer,
            "locked": self.locked,
            "muted": self.muted,
            "hidden": self.hidden,
            "enabled": self.enabled,
            "overlap_policy": (
                self.overlap_policy.value
            ),
            "clip_count": len(
                self.clips
            ),
            "clips": [
                clip.to_dict()
                for clip in self.clips
            ],
            "metadata": deepcopy(
                self.metadata
            ),
        }


@dataclass
class EditableTimeline:
    production_id: str

    version: str = "16.1.4"
    duration: float = 0.0
    fps: float = 30.0

    width: int | None = None
    height: int | None = None

    tracks: list[
        EditableTimelineTrack
    ] = field(
        default_factory=list
    )

    revision: int = 1

    dirty_status: TimelineDirtyStatus = (
        TimelineDirtyStatus.CLEAN
    )

    created_at: str = field(
        default_factory=utc_now_iso
    )
    updated_at: str = field(
        default_factory=utc_now_iso
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        self.production_id = str(
            self.production_id
        ).strip()

        self.duration = max(
            0.0,
            float(self.duration),
        )

        self.fps = float(self.fps)

        if self.fps <= 0:
            self.fps = 30.0

        if not isinstance(
            self.dirty_status,
            TimelineDirtyStatus,
        ):
            self.dirty_status = (
                TimelineDirtyStatus(
                    str(self.dirty_status)
                )
            )

        self.sort_tracks()
        self.recalculate_duration()

    @property
    def minimum_clip_duration(
        self,
    ) -> float:
        return 1.0 / self.fps

    @property
    def dirty(self) -> bool:
        return self.dirty_status in {
            TimelineDirtyStatus.DIRTY,
            TimelineDirtyStatus.SAVE_FAILED,
        }

    @property
    def track_count(self) -> int:
        return len(self.tracks)

    @property
    def clip_count(self) -> int:
        return sum(
            len(track.clips)
            for track in self.tracks
        )

    def sort_tracks(self) -> None:
        self.tracks.sort(
            key=lambda item: (
                item.position,
                item.layer,
                item.track_id,
            )
        )

    def get_track(
        self,
        track_id: str,
    ) -> EditableTimelineTrack | None:
        normalized_id = str(
            track_id
        )

        return next(
            (
                track
                for track in self.tracks
                if track.track_id
                == normalized_id
            ),
            None,
        )

    def get_clip(
        self,
        clip_id: str,
    ) -> EditableTimelineClip | None:
        normalized_id = str(
            clip_id
        )

        for track in self.tracks:
            clip = track.get_clip(
                normalized_id
            )

            if clip is not None:
                return clip

        return None

    def find_clip_track(
        self,
        clip_id: str,
    ) -> EditableTimelineTrack | None:
        normalized_id = str(
            clip_id
        )

        return next(
            (
                track
                for track in self.tracks
                if track.get_clip(
                    normalized_id
                )
                is not None
            ),
            None,
        )

    def all_clips(
        self,
    ) -> list[EditableTimelineClip]:
        return [
            clip
            for track in self.tracks
            for clip in track.clips
        ]

    def recalculate_duration(
        self,
    ) -> float:
        maximum_end = max(
            (
                clip.end_time
                for clip
                in self.all_clips()
            ),
            default=0.0,
        )
        minimum_duration = float(
                self.metadata.get(
                "minimum_duration",
                0.0,
            )
            or 0.0
        )
        self.duration = max(
            minimum_duration,
            maximum_end,
        )
        return self.duration

    def mark_dirty(self) -> None:
        self.revision += 1
        self.dirty_status = (
            TimelineDirtyStatus.DIRTY
        )
        self.updated_at = utc_now_iso()

    def mark_clean(self) -> None:
        self.dirty_status = (
            TimelineDirtyStatus.CLEAN
        )
        self.updated_at = utc_now_iso()

    def clone(
        self,
    ) -> EditableTimeline:
        return deepcopy(self)

    def to_dict(self) -> dict[str, Any]:
        return {
            "production_id": (
                self.production_id
            ),
            "version": self.version,
            "duration": self.duration,
            "fps": self.fps,
            "minimum_clip_duration": (
                self.minimum_clip_duration
            ),
            "width": self.width,
            "height": self.height,
            "track_count": self.track_count,
            "clip_count": self.clip_count,
            "revision": self.revision,
            "dirty": self.dirty,
            "dirty_status": (
                self.dirty_status.value
            ),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "tracks": [
                track.to_dict()
                for track in self.tracks
            ],
            "metadata": deepcopy(
                self.metadata
            ),
        }


@dataclass(frozen=True)
class TimelineEditingIssue:
    code: TimelineEditingIssueCode
    message: str

    clip_id: str | None = None
    track_id: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code.value,
            "message": self.message,
            "clip_id": self.clip_id,
            "track_id": self.track_id,
            "metadata": deepcopy(
                self.metadata
            ),
        }


@dataclass(frozen=True)
class TimelineEditingValidationResult:
    valid: bool

    issues: tuple[
        TimelineEditingIssue,
        ...,
    ] = ()

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def issue_count(self) -> int:
        return len(self.issues)

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "issue_count": (
                self.issue_count
            ),
            "issues": [
                issue.to_dict()
                for issue in self.issues
            ],
            "metadata": deepcopy(
                self.metadata
            ),
        }


@dataclass(frozen=True)
class TimelineEditingEvent:
    operation_type: (
        TimelineEditingOperationType
    )

    production_id: str
    revision: int

    clip_id: str | None = None
    track_id: str | None = None

    before: dict[str, Any] | None = None
    after: dict[str, Any] | None = None

    created_at: str = field(
        default_factory=utc_now_iso
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "operation_type": (
                self.operation_type.value
            ),
            "production_id": (
                self.production_id
            ),
            "revision": self.revision,
            "clip_id": self.clip_id,
            "track_id": self.track_id,
            "before": deepcopy(
                self.before
            ),
            "after": deepcopy(
                self.after
            ),
            "created_at": self.created_at,
            "metadata": deepcopy(
                self.metadata
            ),
        }
       
@dataclass(frozen=True)
class TimelineMutationResult:
    success: bool
    timeline: EditableTimeline

    event: TimelineEditingEvent | None = None

    validation: (
        TimelineEditingValidationResult | None
    ) = None

    changed_clip: (
        EditableTimelineClip | None
    ) = None

    changed_track: (
        EditableTimelineTrack | None
    ) = None

    error: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "timeline": self.timeline.to_dict(),
            "event": (
                self.event.to_dict()
                if self.event
                else None
            ),
            "validation": (
                self.validation.to_dict()
                if self.validation
                else None
            ),
            "changed_clip": (
                self.changed_clip.to_dict()
                if self.changed_clip
                else None
            ),
            "changed_track": (
                self.changed_track.to_dict()
                if self.changed_track
                else None
            ),
            "error": self.error,
            "metadata": deepcopy(
                self.metadata
            ),
        }