from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db.session import SessionLocal
from app.db.models.content_graph import ContentGraph


RUNTIME_KEYS = {
    "editable_timeline",
    "execution_graph",
    "optimized_execution_graph",
    "track_context",
    "subtitle_track",
    "video_track",
    "audio_track",
    "composition",
    "render_instructions",
    "render_plan",
    "render_graph",
    "render_schedule",
    "resolved_assets",
    "ffmpeg_command_plan",
}


def main():
    db = SessionLocal()

    try:
        graphs = db.query(ContentGraph).all()

        found = []

        for graph in graphs:
            try:
                metadata = json.loads(graph.metadata_json or "{}")
            except json.JSONDecodeError:
                metadata = {}

            leaked_keys = sorted(RUNTIME_KEYS.intersection(metadata.keys()))

            if leaked_keys:
                found.append(
                    {
                        "content_graph_id": str(graph.id),
                        "production_id": str(graph.production_id),
                        "leaked_keys": leaked_keys,
                    }
                )

        if not found:
            print("OK: no legacy runtime artifacts found in ContentGraph.metadata_json")
            return

        print("WARNING: legacy runtime artifacts found:")
        for item in found:
            print(item)

    finally:
        db.close()


if __name__ == "__main__":
    main()