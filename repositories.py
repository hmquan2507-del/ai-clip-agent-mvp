import json

from config import DEMO_ACCOUNT_ID, JOBS
from db import db_connect, row_to_dict
from http_utils import safe_name
from utils import now_ts

def save_job(metadata):
    ts = now_ts()
    with db_connect() as conn:
        conn.execute(
            """
            INSERT INTO jobs (
                job_id, account_id, filename, storage_provider, storage_key,
                storage_url, file_size, mime_type, expires_at, width, height, fps, has_audio,
                title, niche, objective, duration,
                clip_count, status, created_at, updated_at, style, mode, target_length, customer_request
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                metadata["job_id"],
                DEMO_ACCOUNT_ID,
                metadata["filename"],
                metadata.get("storage_provider", "local"),
                metadata.get("storage_key", ""),
                metadata.get("storage_url", ""),
                metadata.get("file_size", 0),
                metadata.get("mime_type", ""),
                metadata.get("expires_at"),
                metadata.get("video_analysis", {}).get("width"),
                metadata.get("video_analysis", {}).get("height"),
                metadata.get("video_analysis", {}).get("fps"),
                1 if metadata.get("video_analysis", {}).get("has_audio") else 0,
                metadata["title"],
                metadata["niche"],
                metadata["objective"],
                metadata["duration"],
                len(metadata["suggestions"]),
                "suggested",
                ts,
                ts,
                metadata.get("style", "classic"),
                metadata.get("mode", "auto"),
                metadata.get("target_length", 30),
                metadata.get("customer_request", ""),
            ),
        )
        conn.executemany(
            """
            INSERT INTO suggestions (
                job_id, clip_id, start, duration, hook, caption, cta,
                highlight_score, reason, keywords
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    metadata["job_id"],
                    item["id"],
                    item["start"],
                    item["duration"],
                    item["hook"],
                    item["caption"],
                    item["cta"],
                    item.get("highlight_score", 50),
                    item.get("reason", ""),
                    json.dumps(item.get("keywords", []), ensure_ascii=False),
                )
                for item in metadata["suggestions"]
            ],
        )
        workspace = metadata.get("editor_workspace", {})
        conn.executemany(
            """
            INSERT INTO editor_assets (job_id, asset_type, name, status, source, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    metadata["job_id"],
                    item["type"],
                    item["name"],
                    item["status"],
                    item.get("source", ""),
                    item.get("notes", ""),
                    ts,
                )
                for item in workspace.get("assets", [])
            ],
        )
        conn.executemany(
            """
            INSERT INTO editor_steps (job_id, clip_id, step_order, stage, title, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    metadata["job_id"],
                    step["clip_id"],
                    step["order"],
                    step["stage"],
                    step["title"],
                    step["status"],
                    step.get("notes", ""),
                )
                for step in workspace.get("steps", [])
            ],
        )
        transcript = metadata.get("transcript", {})
        conn.executemany(
            """
            INSERT INTO transcript_segments (job_id, start, end, text, confidence, source, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    metadata["job_id"],
                    segment["start"],
                    segment["end"],
                    segment["text"],
                    segment.get("confidence"),
                    transcript.get("source", "planned"),
                    ts,
                )
                for segment in transcript.get("segments", [])
            ],
        )

def save_outputs(job_id, outputs):
    with db_connect() as conn:
        conn.executemany(
            """
            INSERT INTO outputs (job_id, clip_id, name, url, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            [(job_id, item["id"], item["name"], item["url"], now_ts()) for item in outputs],
        )
        conn.execute(
            "UPDATE jobs SET status = ?, updated_at = ? WHERE job_id = ?",
            ("rendered", now_ts(), job_id),
        )

def enqueue_render_tasks(job_id, selected):
    ts = now_ts()
    with db_connect() as conn:
        for clip_id in selected:
            conn.execute(
                """
                INSERT INTO render_tasks (job_id, clip_id, status, attempts, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (job_id, clip_id, "pending", 0, ts, ts),
            )
        conn.execute(
            "UPDATE jobs SET status = ?, updated_at = ? WHERE job_id = ?",
            ("queued", ts, job_id),
        )

def list_render_tasks(job_id):
    with db_connect() as conn:
        return [
            dict(row)
            for row in conn.execute(
                """
                SELECT *
                FROM render_tasks
                WHERE job_id = ?
                ORDER BY created_at ASC, id ASC
                """,
                (job_id,),
            ).fetchall()
        ]

def list_outputs(job_id):
    with db_connect() as conn:
        rows = [
            dict(row)
            for row in conn.execute(
                """
                SELECT clip_id AS id, name, url, created_at
                FROM outputs
                WHERE job_id = ?
                ORDER BY created_at DESC, id DESC
                """,
                (job_id,),
            ).fetchall()
        ]
    latest = {}
    for row in rows:
        latest.setdefault(int(row["id"]), row)
    return [latest[key] for key in sorted(latest)]

def load_job_payload(job_id):
    job_dir = JOBS / safe_name(job_id)
    metadata_path = job_dir / "job.json"
    if not metadata_path.exists():
        return None
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["outputs"] = list_outputs(job_id)
    metadata["render_tasks"] = list_render_tasks(job_id)
    return metadata

def next_render_task():
    with db_connect() as conn:
        row = conn.execute(
            """
            SELECT *
            FROM render_tasks
            WHERE status = 'pending'
            ORDER BY created_at ASC, id ASC
            LIMIT 1
            """
        ).fetchone()
        if not row:
            return None
        task = dict(row)
        conn.execute(
            """
            UPDATE render_tasks
            SET status = ?, attempts = attempts + 1, updated_at = ?
            WHERE id = ?
            """,
            ("processing", now_ts(), task["id"]),
        )
        return task

def complete_render_task(task_id, output_url):
    with db_connect() as conn:
        conn.execute(
            """
            UPDATE render_tasks
            SET status = ?, output_url = ?, updated_at = ?
            WHERE id = ?
            """,
            ("done", output_url, now_ts(), task_id),
        )

def fail_render_task(task_id, error):
    with db_connect() as conn:
        conn.execute(
            """
            UPDATE render_tasks
            SET status = ?, error = ?, updated_at = ?
            WHERE id = ?
            """,
            ("failed", str(error)[:1000], now_ts(), task_id),
        )

def apply_clip_edits(job_id, metadata, edits):
    if not edits:
        return metadata
    normalized = {int(item["id"]): item for item in edits if item.get("id")}
    if not normalized:
        return metadata
    allowed_fields = {"hook", "caption", "cta"}
    with db_connect() as conn:
        for suggestion in metadata.get("suggestions", []):
            clip_id = int(suggestion["id"])
            edit = normalized.get(clip_id)
            if not edit:
                continue
            for field in allowed_fields:
                if field in edit:
                    suggestion[field] = str(edit.get(field) or "").strip()
            edit_plan = suggestion.setdefault("edit_plan", {})
            for field in ["subtitle_style", "music"]:
                if field in edit:
                    edit_plan[field] = str(edit.get(field) or "").strip()
            for field in ["broll", "sfx"]:
                if field in edit:
                    raw = str(edit.get(field) or "")
                    edit_plan[field] = [item.strip() for item in raw.split("\n") if item.strip()]
            conn.execute(
                """
                UPDATE suggestions
                SET hook = ?, caption = ?, cta = ?
                WHERE job_id = ? AND clip_id = ?
                """,
                (
                    suggestion.get("hook", ""),
                    suggestion.get("caption", ""),
                    suggestion.get("cta", ""),
                    job_id,
                    clip_id,
                ),
            )
    return metadata

def dashboard_payload():
    with db_connect() as conn:
        account = row_to_dict(conn.execute("SELECT * FROM accounts WHERE id = ?", (DEMO_ACCOUNT_ID,)).fetchone())
        total_jobs = conn.execute("SELECT COUNT(*) AS c FROM jobs WHERE account_id = ?", (DEMO_ACCOUNT_ID,)).fetchone()["c"]
        total_outputs = conn.execute(
            """
            SELECT COUNT(*) AS c
            FROM outputs
            JOIN jobs ON jobs.job_id = outputs.job_id
            WHERE jobs.account_id = ?
            """,
            (DEMO_ACCOUNT_ID,),
        ).fetchone()["c"]
        recent = [
            dict(row)
            for row in conn.execute(
                """
                SELECT
                    jobs.*,
                    COALESCE(out_counts.output_count, 0) AS output_count,
                    COALESCE(asset_counts.asset_count, 0) AS asset_count
                FROM jobs
                LEFT JOIN (
                    SELECT job_id, COUNT(*) AS output_count
                    FROM outputs
                    GROUP BY job_id
                ) out_counts ON out_counts.job_id = jobs.job_id
                LEFT JOIN (
                    SELECT job_id, COUNT(*) AS asset_count
                    FROM editor_assets
                    GROUP BY job_id
                ) asset_counts ON asset_counts.job_id = jobs.job_id
                WHERE jobs.account_id = ?
                ORDER BY jobs.created_at DESC
                LIMIT 12
                """,
                (DEMO_ACCOUNT_ID,),
            ).fetchall()
        ]
    used = total_outputs
    account["quota_used"] = used
    account["quota_remaining"] = max(0, account["quota_monthly"] - used)
    return {
        "account": account,
        "stats": {
            "jobs": total_jobs,
            "clips": total_outputs,
            "quota_used": used,
            "quota_monthly": account["quota_monthly"],
            "workspace_modules": 6,
        },
        "recent_jobs": recent,
    }
