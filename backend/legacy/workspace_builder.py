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
