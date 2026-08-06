from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.db.models  # noqa: F401  (registers every table on Base.metadata)
from app.db.base import Base
from app.db.enums import AssetType
from app.db.models.production import Production
from app.db.models.production_asset import ProductionAsset
from app.db.models.user import User
from app.db.models.workspace import Workspace
from app.review.editing.enums import (
    EditableClipType,
    EditableTrackType,
)
from app.review.editing.models import (
    EditableTimeline,
    EditableTimelineClip,
    EditableTimelineTrack,
)
from app.review.persistence import sync_editable_timeline_to_db
from app.services.render_export_service import (
    RenderExportError,
    get_latest_export,
    render_production,
)

SAMPLE_SOURCE_VIDEO = Path(
    "storage/render_artifact_test/"
    "221e4b01-5fb9-4b4a-a549-4fb32c455059/artifacts/final.mp4"
)


def ffprobe(path: Path) -> dict:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-show_entries",
            "stream=width,height,codec_type,codec_name",
            "-of",
            "json",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    import json as _json

    return _json.loads(result.stdout)


def main() -> None:
    if not SAMPLE_SOURCE_VIDEO.exists():
        raise RuntimeError(
            "Sample source video fixture is missing: "
            f"{SAMPLE_SOURCE_VIDEO}. Run "
            "test_render_execution_integration.py first."
        )

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)()

    checks: dict[str, bool] = {}

    # --- Arrange: a real uploaded source video for a real production ---
    user = User(email="operator@example.com")
    db.add(user)
    db.flush()

    workspace = Workspace(name="Test Workspace", owner_id=user.id)
    db.add(workspace)
    db.flush()

    production = Production(
        workspace_id=workspace.id,
        title="Test Production",
    )
    db.add(production)
    db.flush()

    upload_dir = Path("data/uploads") / str(production.id)
    upload_dir.mkdir(parents=True, exist_ok=True)
    uploaded_path = upload_dir / "source.mp4"
    shutil.copyfile(SAMPLE_SOURCE_VIDEO, uploaded_path)

    storage_key = f"{production.id}/source.mp4"

    source_asset = ProductionAsset(
        production_id=production.id,
        type=AssetType.SOURCE_VIDEO,
        filename="source.mp4",
        mime_type="video/mp4",
        storage_path=storage_key,
    )
    db.add(source_asset)
    db.commit()

    source_probe = ffprobe(SAMPLE_SOURCE_VIDEO)
    source_duration = float(source_probe["format"]["duration"])

    # --- Act 1: simulate the operator trimming the clip in the Review
    # Workspace (edit persisted the same way a real timeline command would
    # persist it - see app/review/application/service.py's timeline_sync
    # hook) ---
    trimmed_end = round(source_duration - 3.0, 1)

    timeline = EditableTimeline(
        production_id=str(production.id),
        tracks=[
            EditableTimelineTrack(
                track_id="trk_v1",
                track_type=EditableTrackType.VIDEO_PRIMARY,
                name="Video chính",
                position=0,
                clips=[
                    EditableTimelineClip(
                        clip_id="clip_v1",
                        track_id="trk_v1",
                        clip_type=EditableClipType.VIDEO,
                        start_time=0.0,
                        end_time=trimmed_end,
                        source_start=0.0,
                        source_end=trimmed_end,
                        asset_id=str(source_asset.id),
                    ),
                ],
            ),
        ],
    )
    sync_editable_timeline_to_db(db, timeline)

    # --- Act 2: render, exactly as the real /render/{production_id}
    # endpoint (via RenderRuntimeWorker) now does ---
    try:
        export = render_production(db, production.id)
        render_error: RenderExportError | None = None
    except RenderExportError as error:
        export = None
        render_error = error

    checks["render_succeeded"] = (
        render_error is None and export is not None
    )

    if export is not None:
        checks["export_status_completed"] = (
            export.status == "completed"
        )
        checks["export_has_storage_path"] = bool(
            export.storage_path
        )

        final_path = Path(export.storage_path or "")
        checks["final_file_exists"] = (
            final_path.exists() and final_path.is_file()
        )
        checks["final_file_nonempty"] = (
            final_path.exists()
            and final_path.stat().st_size > 0
        )

        if final_path.exists():
            probe = ffprobe(final_path)
            has_video_stream = any(
                stream.get("codec_type") == "video"
                for stream in probe.get("streams", [])
            )
            checks["final_file_is_playable_video"] = (
                has_video_stream
            )

            rendered_duration = float(
                probe["format"]["duration"]
            )
            # Rendered duration should reflect the trimmed clip
            # (trimmed_end), not the original untrimmed source duration.
            checks["rendered_duration_reflects_trim"] = (
                abs(rendered_duration - trimmed_end) < 2.0
                and rendered_duration < source_duration - 0.5
            )

        latest_export = get_latest_export(db, production.id)
        checks["get_latest_export_matches"] = (
            latest_export is not None
            and latest_export.id == export.id
        )
    else:
        print(
            "render_error:",
            str(render_error),
            getattr(render_error, "issues", None),
        )

    print("=== Review-to-Render Pipeline Integration ===")
    for key, value in checks.items():
        print(f"{key}: {value}")

    import json

    output_path = Path(
        "storage/demo_outputs/"
        "review_render_pipeline_integration.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(checks, indent=2), encoding="utf-8"
    )
    print(f"output: {output_path}")

    db.close()
    shutil.rmtree(upload_dir, ignore_errors=True)

    assert all(checks.values()), checks

    print(
        "\nDONE: Review-to-render pipeline integration "
        "test completed."
    )


if __name__ == "__main__":
    main()
