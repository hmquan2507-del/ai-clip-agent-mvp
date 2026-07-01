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
