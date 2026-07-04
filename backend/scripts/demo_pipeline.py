from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from sqlalchemy import text

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from app.db.enums import MusicMood, QueueStatus, QueueType  # noqa: E402
from app.db.models.production import Production  # noqa: E402
from app.db.models.queue_job import QueueJob  # noqa: E402
from app.db.models.user import User  # noqa: E402
from app.db.models.workspace import Workspace  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.services.broll_service import BrollService  # noqa: E402
from app.services.editing_service import EditingService  # noqa: E402
from app.services.music_service import MusicService  # noqa: E402
from app.services.render_service import RenderService  # noqa: E402
from app.services.sound_effect_service import SoundEffectService  # noqa: E402
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
    workspace = db.query(Workspace).filter(Workspace.owner_id == user.id).first()

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
            "suggests B-roll, adds sound effects, selects background music, "
            "and prepares the final render plan."
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

        sound_effect_plan = SoundEffectService(db).generate_sound_effect_plan(
            production_id=production.id,
        )
        print(f"[OK] Sound Effect plan: {sound_effect_plan.id}")

        music_plan = MusicService(db).generate_music_plan(
            production_id=production.id,
            mood=MusicMood.ENERGETIC,
        )
        print(f"[OK] Music plan: {music_plan.id}")

        render_plan = RenderService(db).generate_render_plan(
            production_id=production.id,
        )
        print(f"[OK] Render plan: {render_plan.id}")

        print("\n=== Counts ===")

        tables = [
            "productions",
            "queue_jobs",
            "editing_plans",
            "editing_plan_items",
            "timelines",
            "timeline_tracks",
            "timeline_clips",
            "subtitles",
            "subtitle_cues",
            "broll_plans",
            "broll_cues",
            "sound_effect_plans",
            "sound_effect_cues",
            "music_plans",
            "music_cues",
            "render_plans",
            "render_tracks",
            "render_assets",
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