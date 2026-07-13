from __future__ import annotations
from app.product.adapters import ProductWorkspaceSnapshot
from app.review.interfaces import ReviewWorkspaceBuilderInterface
from app.review.models import (
    AIState,
    ExportState,
    PreviewState,
    ReviewState,
    ReviewWorkspace,
    SelectionState,
    TimelineState,
)


class ReviewWorkspaceBuilder(ReviewWorkspaceBuilderInterface):
    """
    Builds a ReviewWorkspace from a ProductWorkspaceSnapshot.
    """

    def build_from_snapshot(
        self, snapshot: ProductWorkspaceSnapshot
    ) -> ReviewWorkspace:
        """
        Builds a ReviewWorkspace from a ProductWorkspaceSnapshot.
        """
        preview_state = PreviewState(
            available=snapshot.preview.available,
            video_url=snapshot.preview.video_url,
            thumbnail_url=snapshot.preview.thumbnail_url,
            duration=snapshot.preview.duration,
            width=snapshot.preview.width,
            height=snapshot.preview.height,
            fps=snapshot.preview.fps,
        )

        timeline_state = TimelineState(
            version=snapshot.timeline.version,
            duration=snapshot.timeline.duration,
            track_count=snapshot.timeline.track_count,
            clip_count=snapshot.timeline.clip_count,
            tracks=snapshot.timeline.tracks,
        )

        ai_state = AIState(
            metadata=snapshot.ai_summary,
        )
        
        production_id = (
            snapshot.production.production_id
            if snapshot.production and snapshot.production.production_id
            else "unknown_production"
        )

        return ReviewWorkspace(
            production_id=production_id,
            version=1,
            preview=preview_state,
            timeline=timeline_state,
            review=ReviewState(),
            export=ExportState(),
            ai=ai_state,
            selection=SelectionState(),
            metadata=snapshot.metadata,
        )
