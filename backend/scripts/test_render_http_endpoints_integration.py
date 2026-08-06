from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parents[1])
)

from fastapi.testclient import TestClient
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
from app.db.session import get_db
from app.main import app
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

SAMPLE_SOURCE_VIDEO = Path(
    "storage/render_artifact_test/"
    "221e4b01-5fb9-4b4a-a549-4fb32c455059/artifacts/final.mp4"
)


def main() -> None:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestSessionLocal = sessionmaker(bind=engine)
    db = TestSessionLocal()

    def override_get_db():
        session = TestSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    checks: dict[str, bool] = {}
    upload_dir: Path | None = None

    try:
        user = User(email="http-test@example.com")
        db.add(user)
        db.flush()

        workspace = Workspace(name="HTTP Test Workspace", owner_id=user.id)
        db.add(workspace)
        db.flush()

        production = Production(
            workspace_id=workspace.id,
            title="HTTP Test Production",
        )
        db.add(production)
        db.flush()

        upload_dir = Path("data/uploads") / str(production.id)
        upload_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(
            SAMPLE_SOURCE_VIDEO, upload_dir / "source.mp4"
        )

        source_asset = ProductionAsset(
            production_id=production.id,
            type=AssetType.SOURCE_VIDEO,
            filename="source.mp4",
            mime_type="video/mp4",
            storage_path=f"{production.id}/source.mp4",
        )
        db.add(source_asset)
        db.commit()

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
                            end_time=6.0,
                            source_start=0.0,
                            source_end=6.0,
                            asset_id=str(source_asset.id),
                        ),
                    ],
                ),
            ],
        )
        sync_editable_timeline_to_db(db, timeline)

        client = TestClient(app)

        # Before rendering: download must 404 for real, never fake a
        # sample video.
        pre_download = client.get(
            f"/api/v1/productions/{production.id}/download"
        )
        checks["download_before_render_is_404"] = (
            pre_download.status_code == 404
        )
        checks["download_before_render_not_a_redirect"] = (
            "commondatastorage.googleapis.com"
            not in pre_download.text
        )

        # Submit render through the real, previously-stub-free endpoint.
        # No background worker exists in this app, so this call must
        # actually render inline and return the real outcome.
        render_response = client.post(
            f"/api/v1/render/{production.id}"
        )
        checks["render_endpoint_202"] = (
            render_response.status_code == 202
        )
        render_body = render_response.json()
        print("render_response:", render_body)
        checks["render_status_completed"] = (
            render_body.get("status") == "completed"
        )

        # Download after render must serve the real rendered artifact.
        post_download = client.get(
            f"/api/v1/productions/{production.id}/download"
        )
        checks["download_after_render_200"] = (
            post_download.status_code == 200
        )
        checks["download_content_type_is_video"] = (
            post_download.headers.get("content-type")
            == "video/mp4"
        )
        checks["downloaded_bytes_nonempty"] = (
            len(post_download.content) > 0
        )

        # The submission-runtime / export-workspace path must also
        # auto-run, not just the direct /render/{id} endpoint.
        from app.review.render.checksum import compute_contract_checksum
        from app.review.render.contracts import ReviewRenderContract

        contract = ReviewRenderContract(
            production_id=str(production.id),
            timeline_revision=timeline.revision,
            timeline=timeline.to_dict(),
        )
        checksum = compute_contract_checksum(
            contract.canonical_payload()
        )
        contract_payload = {
            **contract.to_dict(),
            "checksum": checksum,
        }

        submission_response = client.post(
            "/api/v1/export-workspace/render-submissions",
            json=contract_payload,
        )
        checks["export_workspace_submission_202"] = (
            submission_response.status_code == 202
        )
        submission_body = submission_response.json()
        print("submission_response:", submission_body)
        queue_job_id = (
            submission_body.get("data", {}).get("queue_job_id")
        )

        status_response = client.get(
            f"/api/v1/export-workspace/render-submissions/{queue_job_id}"
        )
        status_body = status_response.json()
        print("status_response:", status_body)
        checks["export_workspace_job_auto_ran"] = (
            status_body.get("data", {}).get("status")
            == "completed"
        )

    finally:
        app.dependency_overrides.pop(get_db, None)
        db.close()
        if upload_dir is not None:
            shutil.rmtree(upload_dir, ignore_errors=True)

    print("=== Render HTTP Endpoints Integration ===")
    for key, value in checks.items():
        print(f"{key}: {value}")

    import json

    output_path = Path(
        "storage/demo_outputs/"
        "render_http_endpoints_integration.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(checks, indent=2), encoding="utf-8"
    )
    print(f"output: {output_path}")

    assert all(checks.values()), checks

    print(
        "\nDONE: Render HTTP endpoints integration test "
        "completed."
    )


if __name__ == "__main__":
    main()
