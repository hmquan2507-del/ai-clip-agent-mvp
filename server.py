#!/usr/bin/env python3
import json
import mimetypes
import os
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

from config import JOBS, STATIC
from db import init_db
from http_utils import json_response, parse_multipart, safe_name
from render_queue import process_next_render_task, render_job_clip
from repositories import apply_clip_edits, dashboard_payload, enqueue_render_tasks, list_render_tasks, load_job_payload, save_job
from storage import guess_mime
from storage_helpers import storage_adapter
from suggestions import make_suggestions, normalize_mode
from transcript import transcribe_video
from video_probe import ffprobe_analysis
from workspace_builder import build_editor_workspace


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if path == "/api/dashboard":
            return json_response(self, dashboard_payload())
        if path.startswith("/api/jobs/"):
            job_id = path.removeprefix("/api/jobs/").strip("/")
            payload = load_job_payload(job_id)
            if not payload:
                return json_response(self, {"error": "Không tìm thấy job"}, 404)
            return json_response(self, payload)
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
        job_dir = JOBS / job_id
        stored_file = storage_adapter().save_upload(job_id, filename, file_item["content"])
        original = stored_file.local_path
        if original is None:
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
        metadata = apply_clip_edits(job_id, metadata, payload.get("edits", []))
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
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


if __name__ == "__main__":
    main()
