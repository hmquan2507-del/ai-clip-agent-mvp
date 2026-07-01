import json
import os
import re
import urllib.error
import urllib.request


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
    fallback = lambda: make_heuristic_suggestions(
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
    provider = resolve_ai_provider()
    if not provider:
        return fallback()
    try:
        prompt = build_ai_prompt(duration, clip_count, title, niche, objective, mode, target_length, customer_request, transcript)
        raw = call_ai_provider(provider, prompt)
        suggestions = normalize_ai_suggestions(raw, duration, clip_count, title, niche, objective, mode, target_length, customer_request)
        return suggestions or fallback()
    except Exception:
        return fallback()


def make_heuristic_suggestions(duration, clip_count, title, niche, objective, mode="auto", target_length=30, customer_request="", transcript=None):
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


def resolve_ai_provider():
    provider = os.environ.get("AI_SUGGESTION_PROVIDER", "auto").strip().lower()
    if provider in {"", "off", "none", "heuristic"}:
        return None
    if provider == "auto":
        if os.environ.get("OPENAI_API_KEY"):
            return "openai"
        if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
            return "gemini"
        return None
    if provider == "openai" and os.environ.get("OPENAI_API_KEY"):
        return "openai"
    if provider in {"gemini", "google"} and (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")):
        return "gemini"
    return None


def build_ai_prompt(duration, clip_count, title, niche, objective, mode, target_length, customer_request, transcript):
    effective_mode = normalize_mode(mode, duration)
    desired_count = 1 if effective_mode == "raw_clip" else max(1, min(8, int(clip_count or 3)))
    segments = (transcript or {}).get("segments", [])[:40]
    compact_segments = [
        {
            "start": round(float(segment.get("start", 0)), 2),
            "end": round(float(segment.get("end", 0)), 2),
            "text": str(segment.get("text", ""))[:360],
        }
        for segment in segments
    ]
    return (
        "Bạn là AI Clip Agent cho short-form video tiếng Việt. "
        "Hãy chọn đoạn đáng cắt nhất và viết hook/caption/CTA có tính bán hàng, giữ chân người xem. "
        "Chỉ trả về JSON hợp lệ, không markdown, theo schema: "
        "[{\"start\": number, \"duration\": number, \"hook\": string, \"caption\": string, "
        "\"cta\": string, \"highlight_score\": number, \"reason\": string, \"keywords\": string[], "
        "\"edit_plan\": {\"subtitle_style\": string, \"broll\": string[], \"sfx\": string[], \"music\": string}}]. "
        f"Số clip cần trả về: {desired_count}. "
        f"Độ dài video: {round(float(duration), 2)} giây. "
        f"Mode: {effective_mode}. Độ dài mỗi clip mục tiêu: {target_length} giây. "
        f"Tiêu đề/caption chính: {title or 'chưa có'}. "
        f"Niche: {niche or 'chưa có'}. "
        f"Mục tiêu: {objective or 'chưa có'}. "
        f"Yêu cầu khách: {customer_request or 'chưa có'}. "
        "Nếu transcript là scaffold/fallback thì vẫn chọn theo ngữ cảnh có sẵn. "
        "Không đặt start âm, không vượt quá duration video. "
        "Hook nên ngắn, mạnh, tự nhiên; caption nên rõ lợi ích; CTA nên nhẹ và dễ hành động. "
        f"Transcript segments JSON: {json.dumps(compact_segments, ensure_ascii=False)}"
    )


def call_ai_provider(provider, prompt):
    if provider == "openai":
        return call_openai(prompt)
    if provider == "gemini":
        return call_gemini(prompt)
    raise ValueError("Unsupported AI provider")


def call_openai(prompt):
    api_key = os.environ["OPENAI_API_KEY"]
    model = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
    payload = {
        "model": model,
        "input": prompt,
        "temperature": float(os.environ.get("AI_SUGGESTION_TEMPERATURE", "0.45")),
    }
    data = post_json(
        "https://api.openai.com/v1/responses",
        payload,
        {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    return extract_openai_text(data)


def extract_openai_text(data):
    if isinstance(data, dict) and data.get("output_text"):
        return data["output_text"]
    chunks = []
    for item in data.get("output", []):
        for content in item.get("content", []):
            text = content.get("text") or content.get("output_text")
            if text:
                chunks.append(text)
    return "\n".join(chunks)


def call_gemini(prompt):
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": float(os.environ.get("AI_SUGGESTION_TEMPERATURE", "0.45")),
            "responseMimeType": "application/json",
        },
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    data = post_json(url, payload, {"Content-Type": "application/json"})
    return extract_gemini_text(data)


def extract_gemini_text(data):
    chunks = []
    for candidate in data.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            if part.get("text"):
                chunks.append(part["text"])
    return "\n".join(chunks)


def post_json(url, payload, headers):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    timeout = float(os.environ.get("AI_SUGGESTION_TIMEOUT", "45"))
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"AI provider HTTP {exc.code}: {detail}") from exc


def parse_json_payload(raw):
    text = str(raw or "").strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.IGNORECASE | re.MULTILINE).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"(\[.*\]|\{.*\})", text, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(1))


def normalize_ai_suggestions(raw, duration, clip_count, title, niche, objective, mode, target_length, customer_request):
    payload = parse_json_payload(raw)
    items = payload.get("suggestions", payload) if isinstance(payload, dict) else payload
    if not isinstance(items, list):
        return []
    effective_mode = normalize_mode(mode, duration)
    max_count = 1 if effective_mode == "raw_clip" else max(1, min(8, int(clip_count or 3)))
    target_length = max(8, min(90, float(target_length or 30)))
    results = []
    for item in items[:max_count]:
        if not isinstance(item, dict):
            continue
        start = clamp_number(item.get("start", 0), 0, max(0, float(duration) - 1))
        clip_duration = clamp_number(item.get("duration", target_length), 8, min(90, float(duration)))
        if start + clip_duration > float(duration):
            clip_duration = max(1, float(duration) - start)
        text_for_plan = item.get("hook") or item.get("caption") or title
        score, reason, keywords = score_highlight(text_for_plan, niche, objective, customer_request)
        user_keywords = [str(value).strip() for value in item.get("keywords", []) if str(value).strip()] if isinstance(item.get("keywords"), list) else []
        plan = item.get("edit_plan") if isinstance(item.get("edit_plan"), dict) else {}
        fallback_plan = build_clip_edit_plan(text_for_plan, niche, user_keywords or keywords)
        results.append({
            "id": len(results) + 1,
            "start": round(start, 2),
            "duration": round(clip_duration, 2),
            "hook": str(item.get("hook") or text_for_plan or "Đoạn này đáng cắt thành clip ngắn")[:120],
            "caption": str(item.get("caption") or title or text_for_plan or "AI Clip Agent")[:160],
            "cta": str(item.get("cta") or objective or "Nhắn tin nếu bạn muốn làm video như này")[:120],
            "highlight_score": int(clamp_number(item.get("highlight_score", score), 30, 99)),
            "reason": str(item.get("reason") or reason)[:240],
            "keywords": (user_keywords or keywords)[:8],
            "edit_plan": {
                "subtitle_style": str(plan.get("subtitle_style") or fallback_plan["subtitle_style"]),
                "broll": normalize_string_list(plan.get("broll"), fallback_plan["broll"]),
                "sfx": normalize_string_list(plan.get("sfx"), fallback_plan["sfx"]),
                "music": str(plan.get("music") or fallback_plan["music"]),
            },
        })
    results.sort(key=lambda value: value["highlight_score"], reverse=True)
    for index, suggestion in enumerate(results, start=1):
        suggestion["id"] = index
    return results


def clamp_number(value, low, high):
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = low
    return max(low, min(high, number))


def normalize_string_list(value, fallback):
    if isinstance(value, list):
        items = [str(item).strip() for item in value if str(item).strip()]
        if items:
            return items[:3]
    return fallback[:3]
