from __future__ import annotations

import sys
from pathlib import Path
from uuid import UUID

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db.session import SessionLocal
from app.services.ai_engine_runtime_service import AIEngineRuntimeService
from app.services.asset_resolver_service import AssetResolverService
from app.services.composition_runtime_service import CompositionRuntimeService
from app.services.conflict_resolution_service import ConflictResolutionService
from app.services.execution_graph_service import ExecutionGraphService
from app.services.ffmpeg_runtime_service import FFmpegRuntimeService
from app.services.render_graph_service import RenderGraphService
from app.services.render_instruction_service import RenderInstructionService
from app.services.render_plan_service import RenderPlanService
from app.services.render_schedule_service import RenderScheduleService
from app.services.subtitle_track_composer_service import SubtitleTrackComposerService
from app.services.timeline_composer_service import TimelineComposerService
from app.services.track_context_service import TrackContextService
from app.services.video_track_composer_service import VideoTrackComposerService
from app.services.audio_track_composer_service import AudioTrackComposerService


def run_step(name: str, fn):
    print(f"\n=== {name} ===")
    result = fn()
    metadata = result.get("metadata", {}) if isinstance(result, dict) else {}
    print(f"OK: {name}")
    if metadata:
        print(f"metadata: {metadata}")
    return result


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("python scripts/demo_local_render.py <production_id>")
        raise SystemExit(1)

    production_id = UUID(sys.argv[1])

    db = SessionLocal()

    try:
        ai_runtime = AIEngineRuntimeService(db)

        run_step(
            "AI Brain",
            lambda: ai_runtime.run_pipeline(
                production_id=production_id,
                engine_keys=[
                    "hook_detection",
                    "story_engine",
                    "emotion_engine",
                    "editing_style_engine",
                    "decision_engine",
                    "editing_execution_planner",
                ],
            ),
        )

        run_step(
            "Timeline Composer",
            lambda: TimelineComposerService(db).run(production_id),
        )

        run_step(
            "Execution Graph",
            lambda: ExecutionGraphService(db).run(production_id),
        )

        run_step(
            "Conflict Resolution",
            lambda: ConflictResolutionService(db).run(production_id),
        )

        run_step(
            "Track Context",
            lambda: TrackContextService(db).run(production_id),
        )

        run_step(
            "Subtitle Track",
            lambda: SubtitleTrackComposerService(db).run(production_id),
        )

        run_step(
            "Video Track",
            lambda: VideoTrackComposerService(db).run(production_id),
        )

        run_step(
            "Audio Track",
            lambda: AudioTrackComposerService(db).run(production_id),
        )

        run_step(
            "Composition",
            lambda: CompositionRuntimeService(db).run(production_id),
        )

        run_step(
            "Render Instructions",
            lambda: RenderInstructionService(db).run(production_id),
        )

        run_step(
            "Render Plan",
            lambda: RenderPlanService(db).run(production_id),
        )

        run_step(
            "Render Graph",
            lambda: RenderGraphService(db).run(production_id),
        )

        run_step(
            "Render Schedule",
            lambda: RenderScheduleService(db).run(production_id),
        )

        run_step(
            "Asset Resolver",
            lambda: AssetResolverService(db).run(production_id),
        )

        command_plan = run_step(
            "FFmpeg Command Plan",
            lambda: FFmpegRuntimeService(db).run(production_id),
        )

        print("\n=== FFmpeg Command Preview ===")
        commands = command_plan.get("commands", [])
        if commands:
            print(commands[0].get("command_preview"))
        else:
            print("No FFmpeg command generated.")

        print("\nDONE: Local render demo completed.")

    finally:
        db.close()


if __name__ == "__main__":
    main()