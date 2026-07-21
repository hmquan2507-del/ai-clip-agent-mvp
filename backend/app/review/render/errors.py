class ReviewRenderHandoffError(ValueError):
    code = "review_render_handoff_error"


class DirtyTimelineError(ReviewRenderHandoffError):
    code = "timeline_dirty"


class TimelineRevisionMismatchError(ReviewRenderHandoffError):
    code = "timeline_revision_mismatch"


class InvalidRenderSnapshotError(ReviewRenderHandoffError):
    code = "invalid_render_snapshot"


class RenderSnapshotChecksumError(ReviewRenderHandoffError):
    code = "render_snapshot_checksum_mismatch"
