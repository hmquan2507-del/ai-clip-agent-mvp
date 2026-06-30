#!/usr/bin/env python3
import json
import mimetypes
import os
import re
import sqlite3
import subprocess
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse
from storage import create_storage_adapter, guess_mime

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
DATA = ROOT / "data"
JOBS = ROOT / "data" / "jobs"
DB_PATH = ROOT / "data" / "ai_clip_agent.sqlite3"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DEMO_ACCOUNT_ID = "demo"


def run(cmd):
    return subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)


def now_ts():
    return int(time.time())


def db_connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    DATA.mkdir(parents=True, exist_ok=True)
    JOBS.mkdir(parents=True, exist_ok=True)
    with db_connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                plan TEXT NOT NULL,
                quota_monthly INTEGER NOT NULL,
                created_at INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                storage_provider TEXT NOT NULL DEFAULT 'local',
                storage_key TEXT,
                storage_url TEXT,
                file_size INTEGER NOT NULL DEFAULT 0,
                mime_type TEXT,
                expires_at INTEGER,
                width INTEGER,
                height INTEGER,
                fps REAL,
                has_audio INTEGER NOT NULL DEFAULT 0,
                title TEXT,
                niche TEXT,
                objective TEXT,
                style TEXT NOT NULL DEFAULT 'classic',
                mode TEXT NOT NULL DEFAULT 'auto',
                target_length REAL NOT NULL DEFAULT 30,
                customer_request TEXT,
                duration REAL NOT NULL,
                clip_count INTEGER NOT NULL,
                status TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL,
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            );

            CREATE TABLE IF NOT EXISTS suggestions (
                job_id TEXT NOT NULL,
                clip_id INTEGER NOT NULL,
                start REAL NOT NULL,
                duration REAL NOT NULL,
                hook TEXT NOT NULL,
                caption TEXT NOT NULL,
                cta TEXT NOT NULL,
                highlight_score INTEGER NOT NULL DEFAULT 50,
                reason TEXT,
                keywords TEXT,
                PRIMARY KEY (job_id, clip_id),
                FOREIGN KEY (job_id) REFERENCES jobs(job_id)
            );

            CREATE TABLE IF NOT EXISTS outputs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                clip_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                FOREIGN KEY (job_id) REFERENCES jobs(job_id)
            );

            CREATE TABLE IF NOT EXISTS editor_assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                asset_type TEXT NOT NULL,
                name TEXT NOT NULL,
                status TEXT NOT NULL,
                source TEXT,
                notes TEXT,
                created_at INTEGER NOT NULL,
                FOREIGN KEY (job_id) REFERENCES jobs(job_id)
            );

            CREATE TABLE IF NOT EXISTS editor_steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                clip_id INTEGER NOT NULL,
                step_order INTEGER NOT NULL,
                stage TEXT NOT NULL,
                title TEXT NOT NULL,
                status TEXT NOT NULL,
                notes TEXT,
                FOREIGN KEY (job_id, clip_id) REFERENCES suggestions(job_id, clip_id)
            );

            CREATE TABLE IF NOT EXISTS transcript_segments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                start REAL NOT NULL,
                end REAL NOT NULL,
                text TEXT NOT NULL,
                confidence REAL,
                source TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                FOREIGN KEY (job_id) REFERENCES jobs(job_id)
            );

            CREATE TABLE IF NOT EXISTS render_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                clip_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0,
                error TEXT,
                output_url TEXT,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL,
                FOREIGN KEY (job_id, clip_id) REFERENCES suggestions(job_id, clip_id)
            );
            """
        )
        existing_columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(jobs)").fetchall()
        }
        suggestion_columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(suggestions)").fetchall()
        }
        migrations = {
            "style": "ALTER TABLE jobs ADD COLUMN style TEXT NOT NULL DEFAULT 'classic'",
            "mode": "ALTER TABLE jobs ADD COLUMN mode TEXT NOT NULL DEFAULT 'auto'",
            "target_length": "ALTER TABLE jobs ADD COLUMN target_length REAL NOT NULL DEFAULT 30",
            "customer_request": "ALTER TABLE jobs ADD COLUMN customer_request TEXT",
            "storage_provider": "ALTER TABLE jobs ADD COLUMN storage_provider TEXT NOT NULL DEFAULT 'local'",
            "storage_key": "ALTER TABLE jobs ADD COLUMN storage_key TEXT",
            "storage_url": "ALTER TABLE jobs ADD COLUMN storage_url TEXT",
            "file_size": "ALTER TABLE jobs ADD COLUMN file_size INTEGER NOT NULL DEFAULT 0",
            "mime_type": "ALTER TABLE jobs ADD COLUMN mime_type TEXT",
            "expires_at": "ALTER TABLE jobs ADD COLUMN expires_at INTEGER",
            "width": "ALTER TABLE jobs ADD COLUMN width INTEGER",
            "height": "ALTER TABLE jobs ADD COLUMN height INTEGER",
            "fps": "ALTER TABLE jobs ADD COLUMN fps REAL",
            "has_audio": "ALTER TABLE jobs ADD COLUMN has_audio INTEGER NOT NULL DEFAULT 0",
        }
        for column, statement in migrations.items():
            if column not in existing_columns:
                conn.execute(statement)
        suggestion_migrations = {
            "highlight_score": "ALTER TABLE suggestions ADD COLUMN highlight_score INTEGER NOT NULL DEFAULT 50",
            "reason": "ALTER TABLE suggestions ADD COLUMN reason TEXT",
            "keywords": "ALTER TABLE suggestions ADD COLUMN keywords TEXT",
        }
        for column, statement in suggestion_migrations.items():
            if column not in suggestion_columns:
                conn.execute(statement)
        conn.execute(
            """
            INSERT OR IGNORE INTO accounts (id, name, email, plan, quota_monthly, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (DEMO_ACCOUNT_ID, "Demo Brand", "demo@ai-clip-agent.local", "MVP Trial", 50, now_ts()),
        )


def row_to_dict(row):
    return dict(row) if row else None


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


def render_job_clip(job_id, clip_id):
    job_dir = JOBS / job_id
    metadata_path = job_dir / "job.json"
    if not metadata_path.exists():
        raise FileNotFoundError("Không tìm thấy job")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    input_path = job_dir / metadata["filename"]
    style = metadata.get("style", "classic")
    suggestion = next((item for item in metadata["suggestions"] if int(item["id"]) == int(clip_id)), None)
    if not suggestion:
        raise ValueError("Không tìm thấy clip trong job")
    output_name = f"clip-{suggestion['id']:02d}.mp4"
    output_path = job_dir / output_name
    render_clip(input_path, output_path, suggestion, style=style)
    output = {
        "id": suggestion["id"],
        "name": output_name,
        "url": f"/jobs/{job_id}/{output_name}",
    }
    outputs = metadata.get("outputs", [])
    outputs = [item for item in outputs if int(item["id"]) != int(output["id"])]
    outputs.append(output)
    metadata["outputs"] = sorted(outputs, key=lambda item: item["id"])
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    save_outputs(job_id, [output])
    return output


def process_next_render_task():
    task = next_render_task()
    if not task:
        return None
    try:
        output = render_job_clip(task["job_id"], task["clip_id"])
        complete_render_task(task["id"], output["url"])
        return {"task": task, "output": output}
    except Exception as exc:
        fail_render_task(task["id"], exc)
        raise


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


def ffprobe_duration(path):
    result = run([
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(path),
    ])
    return max(1.0, float(result.stdout.strip()))


def parse_fps(rate):
    if not rate or rate == "0/0":
        return None
    if "/" in rate:
        num, den = rate.split("/", 1)
        den_value = float(den or 1)
        return round(float(num) / den_value, 2) if den_value else None
    return round(float(rate), 2)


def ffprobe_analysis(path):
    result = run([
        "ffprobe",
        "-v",
        "error",
        "-show_streams",
        "-show_format",
        "-of",
        "json",
        str(path),
    ])
    payload = json.loads(result.stdout)
    streams = payload.get("streams", [])
    video = next((stream for stream in streams if stream.get("codec_type") == "video"), {})
    audio = next((stream for stream in streams if stream.get("codec_type") == "audio"), None)
    duration = float(payload.get("format", {}).get("duration") or video.get("duration") or 1)
    width = int(video.get("width") or 0)
    height = int(video.get("height") or 0)
    return {
        "duration": max(1.0, duration),
        "width": width,
        "height": height,
        "aspect_ratio": round(width / height, 3) if width and height else None,
        "fps": parse_fps(video.get("avg_frame_rate") or video.get("r_frame_rate")),
        "video_codec": video.get("codec_name", ""),
        "audio_codec": audio.get("codec_name", "") if audio else "",
        "has_audio": bool(audio),
        "is_vertical": bool(height and width and height > width),
    }


def safe_name(name):
    name = re.sub(r"[^a-zA-Z0-9._-]+", "-", name).strip("-")
    return name or "video.mp4"


def storage_adapter():
    return create_storage_adapter(JOBS)


def wrap(text, limit=24):
    words = str(text or "").strip().split()
    lines = []
    line = []
    length = 0
    for word in words:
        next_len = length + len(word) + (1 if line else 0)
        if line and next_len > limit:
            lines.append(" ".join(line))
            line = [word]
            length = len(word)
        else:
            line.append(word)
            length = next_len
    if line:
        lines.append(" ".join(line))
    return "\n".join(lines[:3])


def drawtext_escape(text, limit=24):
    text = wrap(text, limit=limit)
    return escape_text(text)


def escape_text(text):
    return (
        str(text).replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
        .replace("%", "\\%")
        .replace("\n", "\\n")
    )


def draw_lines(text, limit, max_lines, font_size, y, color="white", border=5):
    lines = wrap(text, limit=limit).splitlines()[:max_lines]
    filters = []
    for index, line in enumerate(lines):
        safe = escape_text(line)
        filters.append(
            f"drawtext=fontfile={FONT}:text='{safe}':fontcolor={color}:fontsize={font_size}:"
            f"x=(w-text_w)/2:y={y + index * int(font_size * 1.12)}:"
            f"borderw={border}:bordercolor=black@0.9"
        )
    return ",".join(filters)


def normalize_mode(mode, duration):
    if mode in {"raw_clip", "long_video"}:
        return mode
    return "raw_clip" if duration <= 90 else "long_video"


def score_highlight(text, niche="", objective="", customer_request=""):
    normalized = str(text or "").lower()
    keyword_groups = {
        "pain": ["khó", "lo", "sai", "mất", "tốn", "vấn đề", "không biết", "kẹt", "lỗi"],
        "value": ["cách", "bí quyết", "lợi ích", "tăng", "giảm", "nhanh", "hiệu quả", "giúp"],
        "money": ["giá", "doanh thu", "bán", "chốt", "đơn", "khách", "inbox", "lợi nhuận"],
        "proof": ["ví dụ", "case", "thực tế", "kết quả", "trước", "sau", "mẫu"],
        "urgency": ["ngay", "hôm nay", "đừng", "nên", "phải", "quan trọng"],
    }
    matched = []
    score = 45
    for words in keyword_groups.values():
        hits = [word for word in words if word in normalized]
        if hits:
            score += min(18, len(hits) * 6)
            matched.extend(hits)
    for value in [niche, objective, customer_request]:
        for word in str(value or "").lower().split():
            if len(word) >= 4 and word in normalized:
                score += 4
                matched.append(word)
    word_count = len(normalized.split())
    if 8 <= word_count <= 36:
        score += 12
    elif word_count > 60:
        score -= 8
    score = max(30, min(98, score))
    reason = "Đoạn có hook rõ, dễ cắt thành clip ngắn."
    if matched:
        reason = "Có tín hiệu nội dung tốt: " + ", ".join(sorted(set(matched))[:5])
    return score, reason, sorted(set(matched))[:8]


def build_clip_edit_plan(text, niche="", keywords=None):
    keywords = keywords or []
    topic = niche or "kinh doanh"
    broll = [
        f"Ảnh/video minh họa ngành {topic}",
        "Close-up màn hình/chat/inbox khi nhắc đến khách hàng",
    ]
    if any(word in keywords for word in ["giá", "doanh thu", "lợi nhuận", "đơn"]):
        broll.append("Overlay số liệu hoặc biểu đồ tăng trưởng")
    if any(word in keywords for word in ["trước", "sau", "ví dụ", "case"]):
        broll.append("Split-screen trước/sau hoặc case study")
    sfx = ["pop nhẹ ở hook đầu", "whoosh ngắn khi đổi ý"]
    if any(word in keywords for word in ["ngay", "đừng", "phải", "quan trọng"]):
        sfx.append("hit sound để nhấn cảnh báo")
    return {
        "subtitle_style": "Caption lớn, 2 dòng, highlight keyword màu vàng",
        "broll": broll[:3],
        "sfx": sfx[:3],
        "music": "Nhạc nền nhẹ, nhịp nhanh vừa, duck dưới giọng nói",
    }


def make_suggestions(duration, clip_count, title, niche, objective, mode="auto", target_length=30, customer_request="", transcript=None):
    mode = normalize_mode(mode, duration)
    target_length = max(8, min(90, float(target_length or 30)))
    transcript_segments = (transcript or {}).get("segments", [])
    if mode == "raw_clip":
        clip_len = round(min(duration, target_length if duration > target_length else duration), 2)
        transcript_text = " ".join(segment["text"] for segment in transcript_segments[:2]).strip()
        score, reason, keywords = score_highlight(transcript_text or title, niche, objective, customer_request)
        return [
            {
                "id": 1,
                "start": 0,
                "duration": clip_len,
                "hook": customer_request or transcript_text[:64] or "Edit clip tho thanh talking head",
                "caption": title or transcript_text[:80] or "Talking head clip",
                "cta": objective or "Theo doi de xem them",
                "highlight_score": score,
                "reason": "Clip thô ngắn nên edit nguyên video." if not reason else reason,
                "keywords": keywords,
                "edit_plan": build_clip_edit_plan(transcript_text or title, niche, keywords),
            }
        ]

    clip_count = max(1, min(8, int(clip_count or 3)))
    clip_len = min(target_length, max(12, duration / max(clip_count, 1)))
    usable = max(1, duration - clip_len)
    hooks = [
        f"Doan nay co the thanh clip hut nguoi xem",
        f"Mot y hay tu video {niche or 'cua ban'}",
        f"Cat rieng doan nay de dang TikTok",
        f"Bien video dai thanh noi dung ngan",
        f"Clip ngan cho {objective or 'xay kenh'}",
        customer_request or "Doan nay hop format talking head",
        "Doan nay nen them caption lon",
        "Phan nay hop lam hook dau video",
        "Dung doan nay de keo nguoi xem",
    ]
    ctas = [
        "Theo doi de xem them",
        "Luu lai de dung khi can",
        "Nhan tin neu ban muon lam video nhu nay",
        "Dang lai moi ngay de xay kenh",
    ]
    suggestions = []
    for i in range(clip_count):
        ratio = (i + 1) / (clip_count + 1)
        start = round(min(usable, usable * ratio), 2)
        if transcript_segments:
            segment = transcript_segments[min(i, len(transcript_segments) - 1)]
            start = round(max(0, min(usable, segment["start"])), 2)
            hook = segment["text"][:76] or hooks[i % len(hooks)]
        else:
            hook = hooks[i % len(hooks)]
        score, reason, keywords = score_highlight(hook, niche, objective, customer_request)
        suggestions.append({
            "id": i + 1,
            "start": start,
            "duration": round(clip_len, 2),
            "hook": hook,
            "caption": title or "AI Clip Agent",
            "cta": ctas[i % len(ctas)],
            "highlight_score": score,
            "reason": reason,
            "keywords": keywords,
            "edit_plan": build_clip_edit_plan(hook, niche, keywords),
        })
    suggestions.sort(key=lambda item: item["highlight_score"], reverse=True)
    for index, suggestion in enumerate(suggestions, start=1):
        suggestion["id"] = index
    return suggestions


def fallback_transcript(duration, title, niche, objective, customer_request):
    seed_lines = [
        title or "Video talking head cua khach",
        customer_request or "Doan nay can bien thanh noi dung ngan de giu chan nguoi xem",
        f"Noi dung phu hop niche {niche or 'kinh doanh'}",
        f"Muc tieu la {objective or 'xay kenh va keo inbox'}",
        "Nen cat thanh cac doan co hook ro, subtitle lon va CTA cuoi video",
    ]
    segment_count = max(1, min(8, int(duration // 20) or 1))
    segment_len = max(8, duration / segment_count)
    segments = []
    for index in range(segment_count):
        start = round(index * segment_len, 2)
        end = round(min(duration, start + segment_len), 2)
        segments.append({
            "start": start,
            "end": end,
            "text": seed_lines[index % len(seed_lines)],
            "confidence": None,
        })
    return {
        "status": "planned",
        "source": "fallback",
        "language": "vi",
        "segments": segments,
        "summary": "Chua co Whisper/faster-whisper nen MVP tao transcript scaffold de editor tiep tuc flow.",
    }


def transcribe_video(input_path, duration, title, niche, objective, customer_request):
    try:
        from faster_whisper import WhisperModel

        model_size = os.environ.get("WHISPER_MODEL", "base")
        model = WhisperModel(model_size, device=os.environ.get("WHISPER_DEVICE", "cpu"), compute_type="int8")
        segments, info = model.transcribe(str(input_path), vad_filter=True)
        rows = []
        for segment in segments:
            text = segment.text.strip()
            if not text:
                continue
            rows.append({
                "start": round(float(segment.start), 2),
                "end": round(float(segment.end), 2),
                "text": text,
                "confidence": None,
            })
        if rows:
            return {
                "status": "ready",
                "source": "faster-whisper",
                "language": getattr(info, "language", "vi"),
                "segments": rows,
                "summary": "Transcript duoc tao bang faster-whisper local.",
            }
    except Exception as exc:
        fallback = fallback_transcript(duration, title, niche, objective, customer_request)
        fallback["summary"] = f"Chua transcribe duoc bang Whisper local: {exc}"
        return fallback
    return fallback_transcript(duration, title, niche, objective, customer_request)


def build_editor_workspace(metadata):
    mode_label = "Edit nguyên video" if metadata["mode"] == "raw_clip" else "Cắt nhiều clip rồi edit từng clip"
    title = metadata.get("title") or metadata["filename"]
    request = metadata.get("customer_request") or "Chưa có yêu cầu riêng"
    target = int(float(metadata.get("target_length") or 30))
    transcript = metadata.get("transcript", {})
    transcript_ready = transcript.get("status") == "ready"
    assets = [
        {
            "type": "footage",
            "name": metadata["filename"],
            "status": "ready",
            "source": "upload",
            "notes": f"{round(metadata['duration'])}s · {mode_label}",
        },
        {
            "type": "subtitle",
            "name": "Auto subtitle track",
            "status": "ready" if transcript_ready else "planned",
            "source": "transcript",
            "notes": transcript.get("summary") or "MVP tạo caption theo hook/caption trước; bước sau nối Whisper để lấy lời nói thật.",
        },
        {
            "type": "broll",
            "name": "B-roll placeholders",
            "status": "planned",
            "source": "editor",
            "notes": f"Gợi ý B-roll theo niche: {metadata.get('niche') or 'chưa chọn'}.",
        },
        {
            "type": "sfx",
            "name": "Sound effect pack",
            "status": "planned",
            "source": "library",
            "notes": "Whoosh/pop/click để nhấn hook, chuyển cảnh và CTA.",
        },
        {
            "type": "music",
            "name": "Background music bed",
            "status": "planned",
            "source": "library",
            "notes": "Nhạc nền nhẹ, tự duck dưới giọng nói.",
        },
    ]
    tracks = [
        {"id": "footage", "name": "Footage", "items": len(metadata["suggestions"]), "status": "ready"},
        {"id": "subtitle", "name": "Subtitle", "items": len(metadata["suggestions"]), "status": "ready" if transcript_ready else "planned"},
        {"id": "broll", "name": "B-roll", "items": max(1, len(metadata["suggestions"]) - 1), "status": "planned"},
        {"id": "sfx", "name": "Sound effect", "items": len(metadata["suggestions"]) * 2, "status": "planned"},
        {"id": "music", "name": "Nhạc nền", "items": 1, "status": "planned"},
    ]
    step_templates = [
        ("footage", "Cắt/crop footage", "ready", f"Chuẩn hóa 1080x1920, format {metadata.get('style', 'talking-head')}."),
        ("subtitle", "Dựng subtitle lớn", "planned", "Caption có hook, nội dung chính, CTA."),
        ("broll", "Gợi ý B-roll", "planned", f"Bám theo nội dung: {title}."),
        ("sfx", "Thêm sound effect", "planned", "Nhấn hook đầu, keyword và chuyển cảnh."),
        ("music", "Thêm nhạc nền", "planned", "Loudness chuẩn social, ưu tiên rõ giọng nói."),
        ("export", "Xuất bản MP4", "ready", f"Render {target}s/clip hoặc theo độ dài clip thô."),
    ]
    steps = []
    for suggestion in metadata["suggestions"]:
        for index, (stage, step_title, status, notes) in enumerate(step_templates, start=1):
            steps.append({
                "clip_id": suggestion["id"],
                "order": index,
                "stage": stage,
                "title": step_title,
                "status": status,
                "notes": notes if stage != "subtitle" else f"{suggestion['hook']} | {suggestion['caption']} | {suggestion['cta']}",
            })
    return {
        "mode_label": mode_label,
        "customer_request": request,
        "assets": assets,
        "tracks": tracks,
        "steps": steps,
        "export_profiles": [
            {"name": "TikTok/Reels/Shorts", "size": "1080x1920", "fps": "30fps", "format": "MP4 H.264"},
            {"name": "Talking head full edit", "size": "1080x1920", "fps": "Nguồn gốc", "format": "MP4 H.264"},
        ],
    }


def parse_multipart(headers, body):
    content_type = headers.get("Content-Type", "")
    match = re.search(r"boundary=(.+)", content_type)
    if not match:
        raise ValueError("Missing multipart boundary")
    boundary = match.group(1).strip().strip('"').encode("utf-8")
    parts = {}
    for chunk in body.split(b"--" + boundary):
        chunk = chunk.strip(b"\r\n")
        if not chunk or chunk == b"--":
            continue
        head, sep, content = chunk.partition(b"\r\n\r\n")
        if not sep:
            continue
        header_text = head.decode("utf-8", errors="replace")
        disposition = ""
        for line in header_text.split("\r\n"):
            if line.lower().startswith("content-disposition:"):
                disposition = line
                break
        name_match = re.search(r'name="([^"]+)"', disposition)
        if not name_match:
            continue
        filename_match = re.search(r'filename="([^"]*)"', disposition)
        name = name_match.group(1)
        if filename_match:
            parts[name] = {
                "filename": filename_match.group(1),
                "content": content.rstrip(b"\r\n"),
            }
        else:
            parts[name] = content.decode("utf-8", errors="replace").strip()
    return parts


def timeline_filter():
    boxes = [
        (32, 1260, 180, 26, "0xf06f6f"),
        (238, 1260, 132, 26, "0x47c6b5"),
        (410, 1260, 190, 26, "0xf06f6f"),
        (636, 1260, 118, 26, "0x47c6b5"),
        (790, 1260, 218, 26, "0xf06f6f"),
        (36, 1320, 250, 28, "0x47c6b5"),
        (318, 1320, 170, 28, "0x47c6b5"),
        (520, 1320, 260, 28, "0x47c6b5"),
        (815, 1320, 210, 28, "0x47c6b5"),
        (42, 1404, 420, 32, "0x0f766e"),
        (486, 1404, 520, 32, "0x0f766e"),
        (42, 1490, 290, 26, "0x1d4ed8"),
        (368, 1490, 240, 26, "0x1d4ed8"),
        (648, 1490, 350, 26, "0x1d4ed8"),
        (42, 1590, 956, 34, "0x0f3f7f"),
    ]
    return ",".join(
        f"drawbox=x={x}:y={y}:w={w}:h={h}:color={color}@0.82:t=fill"
        for x, y, w, h, color in boxes
    )


def render_clip(input_path, output_path, suggestion, style="classic"):
    if style == "raw-edited":
        return render_raw_edited_clip(input_path, output_path, suggestion)
    if style == "talking-head":
        return render_talking_head_clip(input_path, output_path, suggestion)
    return render_classic_clip(input_path, output_path, suggestion)


def render_classic_clip(input_path, output_path, suggestion):
    hook = drawtext_escape(suggestion["hook"])
    caption = drawtext_escape(suggestion["caption"])
    cta = drawtext_escape(suggestion["cta"])
    vf = (
        "scale=1080:-2:force_original_aspect_ratio=increase,"
        "crop=1080:1920,"
        "drawbox=x=0:y=0:w=iw:h=330:color=black@0.50:t=fill,"
        f"drawtext=fontfile={FONT}:text='{hook}':fontcolor=white:fontsize=58:"
        "line_spacing=16:x=(w-text_w)/2:y=82:box=1:boxcolor=black@0.25:boxborderw=22,"
        "drawbox=x=0:y=1515:w=iw:h=405:color=black@0.62:t=fill,"
        f"drawtext=fontfile={FONT}:text='{caption}':fontcolor=white:fontsize=54:"
        "line_spacing=14:x=(w-text_w)/2:y=1580:box=1:boxcolor=black@0.20:boxborderw=18,"
        f"drawtext=fontfile={FONT}:text='{cta}':fontcolor=#ffe066:fontsize=42:"
        "x=(w-text_w)/2:y=1788"
    )
    run([
        "ffmpeg",
        "-y",
        "-ss",
        str(suggestion["start"]),
        "-t",
        str(suggestion["duration"]),
        "-i",
        str(input_path),
        "-vf",
        vf,
        "-af",
        "loudnorm=I=-16:LRA=11:TP=-1.5",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "23",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-movflags",
        "+faststart",
        str(output_path),
    ])


def render_raw_edited_clip(input_path, output_path, suggestion):
    hook = drawtext_escape("EDITED")
    raw_label = drawtext_escape("RAW")
    caption = drawtext_escape(suggestion["caption"])
    cta = drawtext_escape(suggestion["hook"])
    timeline = timeline_filter()
    bg_duration = max(1, float(suggestion["duration"]))
    filter_complex = (
        "[0:v]split=2[rawsrc][editsrc];"
        "[rawsrc]scale=-2:590:force_original_aspect_ratio=increase,crop=330:590,setsar=1[rawv];"
        "[editsrc]scale=530:-2:force_original_aspect_ratio=increase,crop=530:900,setsar=1[editv];"
        f"color=c=0x151515:s=1080x1920:d={bg_duration}[base];"
        "[base]drawgrid=width=120:height=120:thickness=2:color=white@0.18,"
        "drawbox=x=0:y=1180:w=1080:h=740:color=0x111111@0.92:t=fill,"
        f"{timeline},"
        "drawbox=x=70:y=306:w=374:h=670:color=black@0.96:t=fill,"
        "drawbox=x=442:y=224:w=562:h=922:color=0xf5f1e8@0.95:t=fill,"
        f"drawtext=fontfile={FONT}:text='{raw_label}':fontcolor=0xf6e84d:fontsize=62:"
        "x=96:y=194:borderw=4:bordercolor=black@0.7,"
        f"drawtext=fontfile={FONT}:text='{hook}':fontcolor=0xe01b2f:fontsize=60:"
        "x=604:y=104:borderw=8:bordercolor=white@0.95[bg];"
        "[bg][rawv]overlay=92:346[tmp1];"
        "[tmp1][editv]overlay=458:246[tmp2];"
        "[tmp2]drawbox=x=70:y=306:w=374:h=670:color=white@0.7:t=6,"
        "drawbox=x=442:y=224:w=562:h=922:color=white@0.8:t=6,"
        f"drawtext=fontfile={FONT}:text='{caption}':fontcolor=white:fontsize=54:"
        "x=(w-text_w)/2:y=850:borderw=5:bordercolor=black@0.9,"
        f"drawtext=fontfile={FONT}:text='{cta}':fontcolor=0xffe066:fontsize=42:"
        "x=(w-text_w)/2:y=936:borderw=4:bordercolor=black@0.9[v]"
    )
    run([
        "ffmpeg",
        "-y",
        "-ss",
        str(suggestion["start"]),
        "-t",
        str(suggestion["duration"]),
        "-i",
        str(input_path),
        "-filter_complex",
        filter_complex,
        "-map",
        "[v]",
        "-map",
        "0:a?",
        "-af",
        "loudnorm=I=-16:LRA=11:TP=-1.5",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "23",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-shortest",
        "-movflags",
        "+faststart",
        str(output_path),
    ])


def render_talking_head_clip(input_path, output_path, suggestion):
    hook_lines = draw_lines(suggestion["hook"], limit=16, max_lines=2, font_size=46, y=56)
    caption_lines = draw_lines(suggestion["caption"], limit=17, max_lines=2, font_size=56, y=1530)
    cta_lines = draw_lines(suggestion["cta"], limit=22, max_lines=1, font_size=40, y=1772, color="0xffe066", border=4)
    filter_complex = (
        "[0:v]split=2[bgsrc][fgsrc];"
        "[bgsrc]scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,boxblur=18:2,eq=brightness=-0.10:saturation=0.92[bg];"
        "[fgsrc]scale=980:1742:force_original_aspect_ratio=increase,"
        "crop=980:1742,setsar=1[fg];"
        "[bg]drawbox=x=0:y=0:w=1080:h=250:color=black@0.36:t=fill,"
        "drawbox=x=0:y=1490:w=1080:h=430:color=black@0.55:t=fill[base];"
        "[base][fg]overlay=50:130[tmp];"
        "[tmp]drawbox=x=50:y=130:w=980:h=1742:color=white@0.55:t=4,"
        f"{hook_lines},"
        f"{caption_lines},"
        f"{cta_lines},"
        "drawbox=x=0:y=1908:w=1080:h=12:color=white@0.18:t=fill,"
        "drawbox=x=0:y=1908:w=760:h=12:color=0xffe066@0.95:t=fill[v]"
    )
    run([
        "ffmpeg",
        "-y",
        "-ss",
        str(suggestion["start"]),
        "-t",
        str(suggestion["duration"]),
        "-i",
        str(input_path),
        "-filter_complex",
        filter_complex,
        "-map",
        "[v]",
        "-map",
        "0:a?",
        "-af",
        "loudnorm=I=-16:LRA=11:TP=-1.5",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "23",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-shortest",
        "-movflags",
        "+faststart",
        str(output_path),
    ])


def json_response(handler, payload, status=200):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if path == "/api/dashboard":
            return json_response(self, dashboard_payload())
        if path == "/":
            return self.serve_file(STATIC / "index.html")
        if path.startswith("/jobs/"):
            return self.serve_file(JOBS / path.removeprefix("/jobs/"))
        return self.serve_file(STATIC / path.lstrip("/"))

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/upload":
            return self.handle_upload()
        if parsed.path == "/api/uploads/presign":
            return self.handle_presign_upload()
        if parsed.path == "/api/render":
            return self.handle_render()
        return json_response(self, {"error": "Not found"}, 404)

    def handle_presign_upload(self):
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        filename = safe_name(payload.get("filename", "video.mp4"))
        content_type = payload.get("content_type") or guess_mime(filename)
        job_id = f"{int(time.time())}-{uuid.uuid4().hex[:8]}"
        try:
            upload = storage_adapter().create_presigned_upload(job_id, filename, content_type)
        except NotImplementedError:
            return json_response(
                self,
                {
                    "error": "Presigned upload chỉ dùng khi STORAGE_PROVIDER=s3 hoặc r2.",
                    "fallback": "Dùng /api/upload cho local MVP.",
                },
                400,
            )
        except Exception as exc:
            return json_response(self, {"error": str(exc)}, 500)
        return json_response(self, {"job_id": job_id, "filename": filename, **upload})

    def handle_upload(self):
        length = int(self.headers.get("Content-Length", "0"))
        form = parse_multipart(self.headers, self.rfile.read(length))
        file_item = form.get("video")
        if not file_item or not file_item.get("filename"):
            return json_response(self, {"error": "Chưa có file video"}, 400)

        job_id = f"{int(time.time())}-{uuid.uuid4().hex[:8]}"
        filename = safe_name(file_item["filename"])
        stored_file = storage_adapter().save_upload(job_id, filename, file_item["content"])
        original = stored_file.local_path
        if original is None:
            job_dir = JOBS / job_id
            job_dir.mkdir(parents=True, exist_ok=True)
            original = job_dir / filename
            original.write_bytes(file_item["content"])

        title = str(form.get("title", "")).strip()
        niche = str(form.get("niche", "")).strip()
        objective = str(form.get("objective", "")).strip()
        clip_count = str(form.get("clip_count", "3"))
        style = str(form.get("style", "talking-head")).strip() or "talking-head"
        mode = str(form.get("mode", "auto")).strip() or "auto"
        target_length = float(str(form.get("target_length", "30")).strip() or 30)
        customer_request = str(form.get("customer_request", "")).strip()
        video_analysis = ffprobe_analysis(original)
        duration = video_analysis["duration"]
        effective_mode = normalize_mode(mode, duration)
        transcript = transcribe_video(original, duration, title, niche, objective, customer_request)
        suggestions = make_suggestions(
            duration,
            clip_count,
            title,
            niche,
            objective,
            mode=mode,
            target_length=target_length,
            customer_request=customer_request,
            transcript=transcript,
        )
        metadata = {
            "job_id": job_id,
            "filename": stored_file.filename,
            "storage_provider": stored_file.provider,
            "storage_key": stored_file.key,
            "storage_url": stored_file.url,
            "file_size": stored_file.size,
            "mime_type": stored_file.mime_type,
            "expires_at": stored_file.expires_at,
            "duration": duration,
            "video_analysis": {
                **video_analysis,
                "processing_mode": effective_mode,
                "recommended_action": "Edit nguyên video" if effective_mode == "raw_clip" else "Cắt clip rồi edit từng clip",
            },
            "title": title,
            "niche": niche,
            "objective": objective,
            "style": style,
            "mode": effective_mode,
            "target_length": target_length,
            "customer_request": customer_request,
            "transcript": transcript,
            "suggestions": suggestions,
            "outputs": [],
        }
        metadata["editor_workspace"] = build_editor_workspace(metadata)
        save_job(metadata)
        (job_dir / "job.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
        return json_response(self, metadata)

    def handle_render(self):
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        job_id = safe_name(payload.get("job_id", ""))
        selected = set(int(x) for x in payload.get("selected", []))
        job_dir = JOBS / job_id
        metadata_path = job_dir / "job.json"
        if not metadata_path.exists():
            return json_response(self, {"error": "Không tìm thấy job"}, 404)

        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        selected_ids = [
            int(suggestion["id"])
            for suggestion in metadata["suggestions"]
            if not selected or int(suggestion["id"]) in selected
        ]
        if os.environ.get("RENDER_MODE", "sync").lower() == "queue":
            enqueue_render_tasks(job_id, selected_ids)
            return json_response(
                self,
                {
                    "job_id": job_id,
                    "queued": True,
                    "tasks": list_render_tasks(job_id),
                    "message": "Đã đưa clip vào render queue.",
                },
                202,
            )

        outputs = [render_job_clip(job_id, clip_id) for clip_id in selected_ids]
        return json_response(self, {"job_id": job_id, "outputs": outputs})

    def serve_file(self, path):
        try:
            path = path.resolve()
            allowed = [STATIC.resolve(), JOBS.resolve()]
            if not any(path == base or base in path.parents for base in allowed):
                raise FileNotFoundError()
            if not path.exists() or not path.is_file():
                raise FileNotFoundError()
            content_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
            data = path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except FileNotFoundError:
            self.send_error(404)

    def log_message(self, fmt, *args):
        print(f"[{self.log_date_time_string()}] {fmt % args}")


def main():
    init_db()
    port = int(os.environ.get("PORT", "8765"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"AI Clip Agent MVP running at http://localhost:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
