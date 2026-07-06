from __future__ import annotations


SETUP_WORDS = [
    "today", "first", "before", "context", "start",
    "hôm nay", "đầu tiên", "trước khi", "bối cảnh", "bắt đầu",
]

PROBLEM_WORDS = [
    "problem", "mistake", "fail", "hard", "struggle", "pain", "waste",
    "vấn đề", "sai lầm", "thất bại", "khó", "khó khăn", "đau", "lãng phí",
]

INSIGHT_WORDS = [
    "realize", "learned", "truth", "actually", "key", "important",
    "nhận ra", "học được", "sự thật", "thực ra", "chìa khóa", "quan trọng",
]

RESOLUTION_WORDS = [
    "solution", "result", "finally", "therefore", "so", "now",
    "giải pháp", "kết quả", "cuối cùng", "vì vậy", "nên", "bây giờ",
]

PAYOFF_WORDS = [
    "save", "increase", "improve", "achieve", "win", "growth",
    "tiết kiệm", "tăng", "cải thiện", "đạt được", "thắng", "tăng trưởng",
]


def score_story_beat(text: str, start_time: float) -> tuple[str, float, list[str]]:
    normalized = (text or "").lower().strip()

    if not normalized:
        return "unknown", 0.0, ["empty_text"]

    scores: dict[str, float] = {
        "setup": 0.0,
        "problem": 0.0,
        "insight": 0.0,
        "resolution": 0.0,
        "payoff": 0.0,
    }

    reasons: dict[str, list[str]] = {
        "setup": [],
        "problem": [],
        "insight": [],
        "resolution": [],
        "payoff": [],
    }

    if any(word in normalized for word in SETUP_WORDS):
        scores["setup"] += 0.35
        reasons["setup"].append("setup_language")

    if any(word in normalized for word in PROBLEM_WORDS):
        scores["problem"] += 0.45
        reasons["problem"].append("problem_language")

    if any(word in normalized for word in INSIGHT_WORDS):
        scores["insight"] += 0.45
        reasons["insight"].append("insight_language")

    if any(word in normalized for word in RESOLUTION_WORDS):
        scores["resolution"] += 0.40
        reasons["resolution"].append("resolution_language")

    if any(word in normalized for word in PAYOFF_WORDS):
        scores["payoff"] += 0.40
        reasons["payoff"].append("payoff_language")

    if start_time <= 20:
        scores["setup"] += 0.15
        reasons["setup"].append("early_position")

    if "?" in normalized:
        scores["problem"] += 0.15
        scores["insight"] += 0.10
        reasons["problem"].append("question_signal")
        reasons["insight"].append("question_signal")

    if any(char.isdigit() for char in normalized):
        scores["payoff"] += 0.12
        scores["insight"] += 0.08
        reasons["payoff"].append("number_signal")
        reasons["insight"].append("number_signal")

    beat_type = max(scores, key=scores.get)
    score = min(scores[beat_type], 1.0)

    if score <= 0:
        return "unknown", 0.0, ["no_story_signal"]

    return beat_type, round(score, 4), reasons[beat_type]