from __future__ import annotations


EMOTION_KEYWORDS: dict[str, list[str]] = {
    "curiosity": [
        "why", "how", "secret", "truth", "hidden",
        "vì sao", "tại sao", "bí mật", "sự thật", "ít ai biết",
    ],
    "pain": [
        "problem", "mistake", "fail", "struggle", "waste", "hard",
        "vấn đề", "sai lầm", "thất bại", "khó khăn", "lãng phí", "đau",
    ],
    "excitement": [
        "amazing", "powerful", "growth", "win", "breakthrough",
        "tuyệt vời", "mạnh mẽ", "tăng trưởng", "chiến thắng", "đột phá",
    ],
    "trust": [
        "proven", "clear", "simple", "step by step", "safe",
        "đã chứng minh", "rõ ràng", "đơn giản", "từng bước", "an toàn",
    ],
    "urgency": [
        "now", "today", "before", "must", "immediately",
        "ngay bây giờ", "hôm nay", "trước khi", "phải", "ngay lập tức",
    ],
    "surprise": [
        "shocking", "unexpected", "crazy", "unbelievable",
        "sốc", "bất ngờ", "khó tin", "không ngờ",
    ],
}


def score_emotion(text: str, start_time: float) -> tuple[str, float, list[str]]:
    normalized = (text or "").lower().strip()

    if not normalized:
        return "neutral", 0.0, ["empty_text"]

    scores: dict[str, float] = {emotion: 0.0 for emotion in EMOTION_KEYWORDS}
    reasons: dict[str, list[str]] = {emotion: [] for emotion in EMOTION_KEYWORDS}

    for emotion, keywords in EMOTION_KEYWORDS.items():
        matched = [keyword for keyword in keywords if keyword in normalized]

        if matched:
            scores[emotion] += min(0.2 * len(matched), 0.6)
            reasons[emotion].append(f"matched_keywords:{','.join(matched[:3])}")

    if "?" in normalized:
        scores["curiosity"] += 0.18
        reasons["curiosity"].append("question_signal")

    if any(char.isdigit() for char in normalized):
        scores["trust"] += 0.12
        scores["surprise"] += 0.08
        reasons["trust"].append("number_signal")
        reasons["surprise"].append("number_signal")

    if start_time <= 15:
        scores["curiosity"] += 0.08
        reasons["curiosity"].append("early_position")

    emotion = max(scores, key=scores.get)
    intensity = min(scores[emotion], 1.0)

    if intensity <= 0:
        return "neutral", 0.0, ["no_emotion_signal"]

    return emotion, round(intensity, 4), reasons[emotion]