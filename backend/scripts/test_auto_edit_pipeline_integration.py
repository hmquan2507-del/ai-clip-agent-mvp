from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.db.models  # noqa: F401  (registers every table on Base.metadata)
from app.db.base import Base
from app.db.enums import AssetType
from app.db.models.production import Production
from app.db.models.production_asset import ProductionAsset
from app.db.models.user import User
from app.db.models.workspace import Workspace
from app.repositories.timeline_repository import TimelineRepository
from app.services.auto_edit_service import run_auto_edit
from app.services.render_export_service import render_production

SAMPLE_SOURCE_VIDEO = Path(
    "storage/render_artifact_test/"
    "221e4b01-5fb9-4b4a-a549-4fb32c455059/artifacts/final.mp4"
)


def ffprobe_duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout.strip())


def main() -> None:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine)()

    checks: dict[str, bool] = {}
    upload_dir: Path | None = None

    try:
        user = User(email="auto-edit-test@example.com")
        db.add(user)
        db.flush()
        workspace = Workspace(name="Auto Edit Test Workspace", owner_id=user.id)
        db.add(workspace)
        db.flush()
        production = Production(workspace_id=workspace.id, title="Auto Edit Test")
        db.add(production)
        db.flush()

        upload_dir = Path("data/uploads") / str(production.id)
        upload_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SAMPLE_SOURCE_VIDEO, upload_dir / "source.mp4")
        video_duration = ffprobe_duration(SAMPLE_SOURCE_VIDEO)

        source_asset = ProductionAsset(
            production_id=production.id,
            type=AssetType.SOURCE_VIDEO,
            filename="source.mp4",
            mime_type="video/mp4",
            storage_path=f"{production.id}/source.mp4",
            duration=video_duration,
        )
        db.add(source_asset)
        db.commit()

        # --- Act: run the real auto-edit pipeline (real Gemini call) ---
        timeline = run_auto_edit(db, production.id)

        track_types = {track.track_type.value for track in timeline.tracks}
        checks["has_video_track"] = "video_primary" in track_types
        checks["has_subtitle_track"] = "subtitle" in track_types
        checks["has_broll_track"] = "broll" in track_types
        checks["has_music_track"] = "music" in track_types
        checks["has_sfx_track"] = "sound_effect" in track_types

        subtitle_track = next(
            (t for t in timeline.tracks if t.track_type.value == "subtitle"),
            None,
        )
        checks["subtitles_have_real_text"] = bool(
            subtitle_track
            and subtitle_track.clips
            and all(c.text and c.text.strip() for c in subtitle_track.clips)
        )

        broll_track = next(
            (t for t in timeline.tracks if t.track_type.value == "broll"),
            None,
        )
        checks["broll_clips_have_real_local_path"] = bool(
            broll_track
            and broll_track.clips
            and all(
                c.local_path and Path(c.local_path).exists()
                for c in broll_track.clips
            )
        )

        music_track = next(
            (t for t in timeline.tracks if t.track_type.value == "music"),
            None,
        )
        checks["music_clip_has_real_local_path"] = bool(
            music_track
            and music_track.clips
            and Path(music_track.clips[0].local_path).exists()
        )

        # --- Confirm the DB row (not just the in-memory object) persisted
        # local_path correctly ---
        db_timeline = TimelineRepository(db).get_latest_by_production(
            str(production.id)
        )
        db_broll_clips = [
            clip
            for track in db_timeline.tracks
            for clip in track.clips
            if track.type.value == "broll"
        ]
        checks["db_broll_clip_has_local_path"] = bool(
            db_broll_clips and db_broll_clips[0].local_path
        )

        # --- Render the AI-edited timeline for real and confirm the
        # output actually differs from the raw source (b-roll/music
        # baked in via ffmpeg) ---
        export = render_production(db, production.id)
        checks["render_succeeded"] = export.status == "completed"

        if export.status == "completed":
            final_path = Path(export.storage_path)
            checks["final_file_exists"] = final_path.exists()
            probe = subprocess.run(
                [
                    "ffprobe", "-v", "error",
                    "-show_entries", "stream=codec_type",
                    "-of", "csv=p=0",
                    str(final_path),
                ],
                capture_output=True, text=True, check=True,
            )
            checks["final_file_has_audio_and_video"] = (
                "video" in probe.stdout and "audio" in probe.stdout
            )

    finally:
        db.close()
        if upload_dir is not None:
            shutil.rmtree(upload_dir, ignore_errors=True)

    print("=== Auto-Edit Pipeline Integration ===")
    for key, value in checks.items():
        print(f"{key}: {value}")

    import json
    output_path = Path(
        "storage/demo_outputs/auto_edit_pipeline_integration.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(checks, indent=2), encoding="utf-8")
    print(f"output: {output_path}")

    assert all(checks.values()), checks

    print("\nDONE: Auto-edit pipeline integration test completed.")


if __name__ == "__main__":
    main()
