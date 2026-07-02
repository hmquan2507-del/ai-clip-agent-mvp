import json

from utils import run

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
