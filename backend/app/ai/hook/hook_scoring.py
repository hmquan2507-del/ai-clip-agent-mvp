from __future__ import annotations


QUESTION_WORDS = [
    "why", "how", "what", "when", "where",
    "vì sao", "tại sao", "như thế nào", "làm sao", "bạn có biết",
]

CURIOSITY_PHRASES = [
    "secret", "truth", "hidden", "unknown",
    "bí mật", "sự thật", "ít ai biết", "không ai nói", "bạn chưa biết",
]

EMOTIONAL_WORDS = [
    "shocking", "amazing", "terrible", "crazy", "powerful",
    "sốc", "bất ngờ", "đáng sợ", "tuyệt vời", "mạnh mẽ", "khó tin",
]

PAIN_POINT_WORDS = [
    "problem", "mistake", "fail", "struggle", "waste",
    "vấn đề", "sai lầm", "thất bại", "khó khăn", "lãng phí", "không hiệu quả",
]

PROMISE_WORDS = [
    "learn", "achieve", "improve", "save", "increase",
    "học được", "đạt được", "cải thiện", "tiết kiệm", "tăng", "giúp bạn",
]

CONTRAST_WORDS = [
    "but", "however", "instead", "although",
    "nhưng", "tuy nhiên", "thay vì", "mặc dù",
]


def score_hook_segment(text: str, start_time: float) -> tuple[float, list[str]]:
    normalized = (text or "").lower().strip()

    score = 0.0
    reasons: list[str] = []

    if not normalized:
        return 0.0, ["empty_text"]

    if "?" in normalized or any(word in normalized for word in QUESTION_WORDS):
        score += 0.22
        reasons.append("question_hook")

    if any(phrase in normalized for phrase in CURIOSITY_PHRASES):
        score += 0.18
        reasons.append("curiosity_phrase")

    if any(word in normalized for word in EMOTIONAL_WORDS):
        score += 0.15
        reasons.append("emotional_language")

    if any(word in normalized for word in PAIN_POINT_WORDS):
        score += 0.18
        reasons.append("pain_point")

    if any(word in normalized for word in PROMISE_WORDS):
        score += 0.16
        reasons.append("promise_or_result")

    if any(char.isdigit() for char in normalized):
        score += 0.12
        reasons.append("number_or_statistic")

    if any(word in normalized for word in CONTRAST_WORDS):
        score += 0.10
        reasons.append("contrast")

    if start_time <= 15:
        score += 0.16
        reasons.append("early_position")

    if len(normalized) < 12:
        score -= 0.10
        reasons.append("too_short")

    return max(0.0, min(score, 1.0)), reasons