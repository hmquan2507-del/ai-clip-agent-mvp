from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from sqlalchemy import text
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from app.db.enums import QueueStatus, QueueType  # noqa: E402
from app.db.models.production import Production  # noqa: E402
from app.db.models.queue_job import QueueJob  # noqa: E402
from app.db.models.user import User  # noqa: E402
from app.db.models.workspace import Workspace  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.repositories.queue_repository import QueueRepository  # noqa: E402
from app.services.broll_service import BrollService  # noqa: E402
from app.services.editing_service import EditingService  # noqa: E402
from app.services.subtitle_service import SubtitleService  # noqa: E402
from app.services.timeline_service import TimelineService  # noqa: E402


DEMO_EMAIL = "demo@aiclipagent.local"


def get_or_create_demo_user(db):
    user = db.query(User).filter(User.email == DEMO_EMAIL).first()

    if user:
        return user

    user = User(
        email=DEMO_EMAIL,
        name="Demo User",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_or_create_demo_workspace(db, user):
    workspace = (
        db.query(Workspace)
        .filter(Workspace.owner_id == user.id)
        .first()
    )

    if workspace:
        return workspace

    workspace = Workspace(
        owner_id=user.id,
        name="Demo Workspace",
    )

    db.add(workspace)
    db.commit()
    db.refresh(workspace)

    return workspace


def create_demo_production(db, workspace):
    production = Production(
        workspace_id=workspace.id,
        title="Demo Pipeline Production",
        description="End-to-end demo pipeline for EPIC 7.",
        style="short_form",
    )

    db.add(production)
    db.commit()
    db.refresh(production)

    return production


def create_completed_transcript_job(db, production):
    transcript_result = {
        "text": (
            "In this video, I will show you how AI Clip Agent turns raw video "
            "into a ready-to-post short-form clip. First, it reads the transcript. "
            "Then it finds the strongest hook, removes boring parts, adds subtitles, "
            "suggests B-roll, and prepares the timeline for rendering."
        )
    }

    job = QueueJob(
        production_id=production.id,
        type=QueueType.TRANSCRIPT,
        status=QueueStatus.COMPLETED,
        progress=100,
        payload=json.dumps({}),
        result=json.dumps(transcript_result, ensure_ascii=False),
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


async def run_pipeline():
    db = SessionLocal()

    try:
        print("\n=== AI Clip Agent Demo Pipeline ===")

        user = get_or_create_demo_user(db)
        workspace = get_or_create_demo_workspace(db, user)
        production = create_demo_production(db, workspace)
        transcript_job = create_completed_transcript_job(db, production)

        print(f"[OK] User: {user.id}")
        print(f"[OK] Workspace: {workspace.id}")
        print(f"[OK] Production: {production.id}")
        print(f"[OK] Transcript job: {transcript_job.id}")

        editing_plan = await EditingService(db).generate_editing_plan(
            production_id=production.id,
            provider="mock",
            target_duration_seconds=60,
        )
        print(f"[OK] Editing plan: {editing_plan.id}")

        timeline = TimelineService(db).generate_timeline(
            production_id=production.id,
        )
        print(f"[OK] Timeline: {timeline.id}")

        subtitle = SubtitleService(db).generate_subtitle(
            production_id=production.id,
        )
        print(f"[OK] Subtitle: {subtitle.id}")

        broll_plan = BrollService(db).generate_broll_plan(
            production_id=production.id,
        )
        print(f"[OK] B-roll plan: {broll_plan.id}")

        print("\n=== Counts ===")
        tables = [
            "editing_plans",
            "editing_plan_items",
            "timelines",
            "timeline_tracks",
            "timeline_clips",
            "subtitles",
            "subtitle_cues",
            "broll_plans",
            "broll_cues",
        ]

        for table in tables:
            count = db.execute(
    text(f"SELECT COUNT(*) FROM {table}")
).scalar()
            print(f"{table}: {count}")

        print("\nDEMO PIPELINE COMPLETED\n")

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(run_pipeline())