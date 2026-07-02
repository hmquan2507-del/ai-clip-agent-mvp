import json
import re

def safe_name(name):
    name = re.sub(r"[^a-zA-Z0-9._-]+", "-", name).strip("-")
    return name or "video.mp4"

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

def json_response(handler, payload, status=200):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)
