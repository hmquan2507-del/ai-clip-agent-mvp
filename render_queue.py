import json

from config import JOBS
from rendering import render_clip
from repositories import complete_render_task, fail_render_task, next_render_task, save_outputs

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
