import os

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
