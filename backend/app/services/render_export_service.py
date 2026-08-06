from __future__ import annotations

from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.enums import ExportStatus
from app.db.models.export import Export
from app.render.production.factory import (
    build_production_render_runtime,
)
from app.review.render.timeline_adapter import (
    TimelineAdapterError,
    build_execution_timeline_for_production,
)

RENDER_STORAGE_ROOT = "storage/production_render"


class RenderExportError(RuntimeError):
    def __init__(self, message: str, *, issues: list[str] | None = None):
        super().__init__(message)
        self.issues = issues or []


def render_production(
    db: Session,
    production_id: UUID | str,
) -> Export:
    """Render the production's current edited timeline for real and record
    the result as an Export row.

    This is the one place that turns "operator edited a timeline in the
    Review Workspace" into "a real MP4 exists on disk" - it reuses the
    already-working render/execution machinery (app/render/production,
    app/render/execution, app/timeline/compiler) end to end, including a
    real ffmpeg subprocess and the quality gate; it does not re-implement
    any of that.
    """
    normalized_id = str(production_id)

    export = Export(
        production_id=normalized_id,
        status=ExportStatus.RENDERING,
        format="mp4",
    )
    db.add(export)
    db.commit()
    db.refresh(export)

    try:
        execution_timeline = build_execution_timeline_for_production(
            db, normalized_id
        )
    except TimelineAdapterError as error:
        export.status = ExportStatus.FAILED
        db.commit()
        raise RenderExportError(str(error)) from error

    runtime = build_production_render_runtime()
    result = runtime.render(
        execution_timeline=execution_timeline,
        storage_root=RENDER_STORAGE_ROOT,
    )

    if not result.success or not result.final_video_path:
        export.status = ExportStatus.FAILED
        db.commit()
        raise RenderExportError(
            "Render failed.",
            issues=[issue.message for issue in result.issues],
        )

    final_path = Path(result.final_video_path)

    export.status = ExportStatus.COMPLETED
    export.storage_path = str(final_path)
    export.resolution = (
        f"{execution_timeline.width}x{execution_timeline.height}"
    )
    export.file_size_bytes = (
        final_path.stat().st_size if final_path.exists() else None
    )

    db.commit()
    db.refresh(export)

    return export


def get_latest_export(
    db: Session,
    production_id: UUID | str,
) -> Export | None:
    return (
        db.query(Export)
        .filter(Export.production_id == str(production_id))
        .order_by(Export.created_at.desc())
        .first()
    )
