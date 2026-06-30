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
            """
        )
        existing_columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(jobs)").fetchall()
        }
        migrations = {
            "style": "ALTER TABLE jobs ADD COLUMN style TEXT NOT NULL DEFAULT 'classic'",
            "mode": "ALTER TABLE jobs ADD COLUMN mode TEXT NOT NULL DEFAULT 'auto'",
            "target_length": "ALTER TABLE jobs ADD COLUMN target_length REAL NOT NULL DEFAULT 30",
            "customer_request": "ALTER TABLE jobs ADD COLUMN customer_request TEXT",
        }
        for column, statement in migrations.items():
            if column not in existing_columns:
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
                job_id, account_id, filename, title, niche, objective, duration,
                clip_count, status, created_at, updated_at, style, mode, target_length, customer_request
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                metadata["job_id"],
                DEMO_ACCOUNT_ID,
                metadata["filename"],
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
            INSERT INTO suggestions (job_id, clip_id, start, duration, hook, caption, cta)
            VALUES (?, ?, ?, ?, ?, ?, ?)
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


def safe_name(name):
    name = re.sub(r"[^a-zA-Z0-9._-]+", "-", name).strip("-")
    return name or "video.mp4"


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


def make_suggestions(duration, clip_count, title, niche, objective, mode="auto", target_length=30, customer_request=""):
    mode = normalize_mode(mode, duration)
    target_length = max(8, min(90, float(target_length or 30)))
    if mode == "raw_clip":
        clip_len = round(min(duration, target_length if duration > target_length else duration), 2)
        return [
            {
                "id": 1,
                "start": 0,
                "duration": clip_len,
                "hook": customer_request or "Edit clip tho thanh talking head",
                "caption": title or "Talking head clip",
                "cta": objective or "Theo doi de xem them",
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
        suggestions.append({
            "id": i + 1,
            "start": start,
            "duration": round(clip_len, 2),
            "hook": hooks[i % len(hooks)],
            "caption": title or "AI Clip Agent",
            "cta": ctas[i % len(ctas)],
        })
    return suggestions


def build_editor_workspace(metadata):
    mode_label = "Edit nguyên video" if metadata["mode"] == "raw_clip" else "Cắt nhiều clip rồi edit từng clip"
    title = metadata.get("title") or metadata["filename"]
    request = metadata.get("customer_request") or "Chưa có yêu cầu riêng"
    target = int(float(metadata.get("target_length") or 30))
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
            "status": "planned",
            "source": "transcript",
            "notes": "MVP tạo caption theo hook/caption trước; bước sau nối Whisper để lấy lời nói thật.",
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
        {"id": "subtitle", "name": "Subtitle", "items": len(metadata["suggestions"]), "status": "planned"},
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
        if parsed.path == "/api/render":
            return self.handle_render()
        return json_response(self, {"error": "Not found"}, 404)

    def handle_upload(self):
        length = int(self.headers.get("Content-Length", "0"))
        form = parse_multipart(self.headers, self.rfile.read(length))
        file_item = form.get("video")
        if not file_item or not file_item.get("filename"):
            return json_response(self, {"error": "Chưa có file video"}, 400)

        job_id = f"{int(time.time())}-{uuid.uuid4().hex[:8]}"
        job_dir = JOBS / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        original = job_dir / safe_name(file_item["filename"])
        with original.open("wb") as f:
            f.write(file_item["content"])

        title = str(form.get("title", "")).strip()
        niche = str(form.get("niche", "")).strip()
        objective = str(form.get("objective", "")).strip()
        clip_count = str(form.get("clip_count", "3"))
        style = str(form.get("style", "talking-head")).strip() or "talking-head"
        mode = str(form.get("mode", "auto")).strip() or "auto"
        target_length = float(str(form.get("target_length", "30")).strip() or 30)
        customer_request = str(form.get("customer_request", "")).strip()
        duration = ffprobe_duration(original)
        effective_mode = normalize_mode(mode, duration)
        suggestions = make_suggestions(
            duration,
            clip_count,
            title,
            niche,
            objective,
            mode=mode,
            target_length=target_length,
            customer_request=customer_request,
        )
        metadata = {
            "job_id": job_id,
            "filename": original.name,
            "duration": duration,
            "title": title,
            "niche": niche,
            "objective": objective,
            "style": style,
            "mode": effective_mode,
            "target_length": target_length,
            "customer_request": customer_request,
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
        input_path = job_dir / metadata["filename"]
        style = metadata.get("style", "classic")
        outputs = []
        for suggestion in metadata["suggestions"]:
            if selected and suggestion["id"] not in selected:
                continue
            output_name = f"clip-{suggestion['id']:02d}.mp4"
            output_path = job_dir / output_name
            render_clip(input_path, output_path, suggestion, style=style)
            outputs.append({
                "id": suggestion["id"],
                "name": output_name,
                "url": f"/jobs/{job_id}/{output_name}",
            })
        metadata["outputs"] = outputs
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
        save_outputs(job_id, outputs)
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
