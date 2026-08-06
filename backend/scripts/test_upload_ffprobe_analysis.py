from __future__ import annotations

import io
import shutil
import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from fastapi import UploadFile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.db.models  # noqa: F401  (registers every table on Base.metadata)
from app.db.base import Base
from app.db.models.production import Production
from app.db.models.user import User
from app.db.models.workspace import Workspace
from app.services.upload_service import UploadService
from app.services.upload_validation_service import UploadValidationError

SAMPLE_SOURCE_VIDEO = Path(
    "storage/render_artifact_test/"
    "221e4b01-5fb9-4b4a-a549-4fb32c455059/artifacts/final.mp4"
)


def main() -> None:
    if not SAMPLE_SOURCE_VIDEO.exists():
        raise RuntimeError(
            "Sample source video fixture is missing: "
            f"{SAMPLE_SOURCE_VIDEO}."
        )

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
        user = User(email="ffprobe-test@example.com")
        db.add(user)
        db.flush()

        workspace = Workspace(name="FFprobe Test Workspace", owner_id=user.id)
        db.add(workspace)
        db.flush()

        production = Production(
            workspace_id=workspace.id,
            title="FFprobe Test Production",
        )
        db.add(production)
        db.commit()

        service = UploadService(db)

        # --- Case 1: a real video upload gets real ffprobe metadata ---
        with open(SAMPLE_SOURCE_VIDEO, "rb") as fh:
            upload_file = UploadFile(
                file=io.BytesIO(fh.read()),
                filename="real_video.mp4",
                headers={"content-type": "video/mp4"},
            )

        asset = service.upload_source_video(
            production.id, upload_file
        )
        upload_dir = Path("data/uploads") / str(production.id)

        checks["duration_populated"] = (
            asset.duration is not None and asset.duration > 0
        )
        checks["width_populated"] = asset.width == 1080
        checks["height_populated"] = asset.height == 1920
        checks["fps_populated"] = (
            asset.fps is not None and asset.fps > 0
        )
        checks["video_codec_populated"] = (
            asset.video_codec == "h264"
        )
        checks["audio_codec_populated"] = (
            asset.audio_codec == "aac"
        )
        checks["has_audio_true"] = asset.has_audio is True

        # --- Case 2: a non-video file must be rejected, not silently
        # accepted with empty metadata ---
        garbage_file = UploadFile(
            file=io.BytesIO(b"this is not a real video file"),
            filename="not_a_video.mp4",
            headers={"content-type": "video/mp4"},
        )

        rejected = False
        try:
            service.upload_source_video(
                production.id, garbage_file
            )
        except UploadValidationError:
            rejected = True

        checks["invalid_file_rejected"] = rejected

        # And it must not have left an orphaned file behind.
        leftover_files = list(upload_dir.glob("*not_a_video*"))
        checks["rejected_upload_file_cleaned_up"] = (
            len(leftover_files) == 0
        )

    finally:
        db.close()
        if upload_dir is not None:
            shutil.rmtree(upload_dir, ignore_errors=True)

    print("=== Upload FFprobe Analysis ===")
    for key, value in checks.items():
        print(f"{key}: {value}")

    import json

    output_path = Path(
        "storage/demo_outputs/upload_ffprobe_analysis.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(checks, indent=2), encoding="utf-8"
    )
    print(f"output: {output_path}")

    assert all(checks.values()), checks

    print("\nDONE: Upload ffprobe analysis test completed.")


if __name__ == "__main__":
    main()
