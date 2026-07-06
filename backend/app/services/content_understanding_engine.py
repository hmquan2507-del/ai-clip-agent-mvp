from __future__ import annotations

import json
import re

from app.db.enums import ContentEmotion, ContentSegmentType


class ContentUnderstandingEngine:
    def build_from_transcript(
        self,
        transcript_text: str,
        language: str | None = "vi",
    ) -> dict:
        chunks = self._split_transcript(transcript_text)

        segments: list[dict] = []

        for index, chunk in enumerate(chunks):
            segment_type = self._detect_segment_type(chunk, index)
            emotion = self._detect_emotion(chunk)
            importance_score = self._score_importance(chunk, segment_type)
            viral_score = self._score_viral_potential(chunk, segment_type, emotion)

            segments.append(
                {
                    "start_time": float(index * 8),
                    "end_time": float((index + 1) * 8),
                    "text": chunk,
                    "type": segment_type,
                    "emotion": emotion,
                    "topic": self._detect_topic(chunk),
                    "importance_score": importance_score,
                    "viral_potential_score": viral_score,
                    "speaker_id": "speaker_1",
                    "order_index": index,
                    "metadata_json": self.dumps_json(
                        {
                            "engine": "rule_based_v1",
                            "word_count": len(chunk.split()),
                        }
                    ),
                }
            )

        return {
            "language": language,
            "summary": self._build_summary(transcript_text),
            "topics": self._build_topics(segments),
            "speakers": [{"id": "speaker_1", "role": "unknown"}],
            "segments": segments,
            "metadata": {
                "engine": "content_understanding_rule_based_v1",
                "segment_count": len(segments),
            },
        }

    def _split_transcript(self, text: str) -> list[str]:
        sentences = re.split(r"(?<=[.!?。！？])\s+", text.strip())
        sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

        if not sentences:
            return []

        chunks: list[str] = []
        current: list[str] = []

        for sentence in sentences:
            current.append(sentence)

            if len(" ".join(current).split()) >= 20:
                chunks.append(" ".join(current))
                current = []

        if current:
            chunks.append(" ".join(current))

        return chunks

    def _detect_segment_type(
        self,
        text: str,
        index: int,
    ) -> ContentSegmentType:
        lowered = text.lower()

        if index == 0:
            return ContentSegmentType.INTRO

        if any(word in lowered for word in ["subscribe", "follow", "comment", "đăng ký", "theo dõi"]):
            return ContentSegmentType.CTA

        if any(word in lowered for word in ["for example", "ví dụ", "chẳng hạn"]):
            return ContentSegmentType.EXAMPLE

        if any(word in lowered for word in ["story", "câu chuyện", "lúc đó", "ngày xưa"]):
            return ContentSegmentType.STORY

        if any(word in lowered for word in ["why", "how", "tại sao", "làm thế nào", "bí mật"]):
            return ContentSegmentType.HOOK

        if len(text.split()) < 6:
            return ContentSegmentType.FILLER

        return ContentSegmentType.MAIN_POINT

    def _detect_emotion(self, text: str) -> ContentEmotion:
        lowered = text.lower()

        if any(word in lowered for word in ["wow", "amazing", "không ngờ", "bất ngờ"]):
            return ContentEmotion.SURPRISED

        if any(word in lowered for word in ["haha", "funny", "buồn cười", "hài"]):
            return ContentEmotion.FUNNY

        if any(word in lowered for word in ["important", "quan trọng", "nghiêm túc"]):
            return ContentEmotion.SERIOUS

        if any(word in lowered for word in ["inspire", "truyền cảm hứng", "thành công"]):
            return ContentEmotion.INSPIRATIONAL

        if any(word in lowered for word in ["angry", "tức", "bực"]):
            return ContentEmotion.ANGRY

        if any(word in lowered for word in ["excited", "hào hứng", "tuyệt vời"]):
            return ContentEmotion.EXCITED

        return ContentEmotion.NEUTRAL

    def _score_importance(
        self,
        text: str,
        segment_type: ContentSegmentType,
    ) -> float:
        base = min(len(text.split()) / 40, 1.0)

        bonus = {
            ContentSegmentType.HOOK: 0.25,
            ContentSegmentType.MAIN_POINT: 0.2,
            ContentSegmentType.STORY: 0.15,
            ContentSegmentType.EXAMPLE: 0.1,
            ContentSegmentType.CTA: 0.05,
            ContentSegmentType.FILLER: -0.25,
        }.get(segment_type, 0)

        return round(max(0, min(base + bonus, 1.0)), 2)

    def _score_viral_potential(
        self,
        text: str,
        segment_type: ContentSegmentType,
        emotion: ContentEmotion,
    ) -> float:
        score = 0.3

        if segment_type == ContentSegmentType.HOOK:
            score += 0.35

        if segment_type in {ContentSegmentType.STORY, ContentSegmentType.MAIN_POINT}:
            score += 0.2

        if emotion in {
            ContentEmotion.EXCITED,
            ContentEmotion.SURPRISED,
            ContentEmotion.FUNNY,
            ContentEmotion.INSPIRATIONAL,
        }:
            score += 0.2

        if any(word in text.lower() for word in ["secret", "bí mật", "sai lầm", "truth", "sự thật"]):
            score += 0.15

        return round(max(0, min(score, 1.0)), 2)

    def _detect_topic(self, text: str) -> str | None:
        lowered = text.lower()

        topic_keywords = {
            "ai": ["ai", "artificial intelligence", "trí tuệ nhân tạo"],
            "business": ["business", "startup", "kinh doanh", "doanh nghiệp"],
            "marketing": ["marketing", "content", "tiktok", "viral"],
            "productivity": ["productivity", "năng suất", "workflow", "quy trình"],
            "money": ["money", "tiền", "doanh thu", "lợi nhuận"],
        }

        for topic, keywords in topic_keywords.items():
            if any(keyword in lowered for keyword in keywords):
                return topic

        return "general"

    def _build_summary(self, text: str) -> str:
        words = text.split()
        if len(words) <= 40:
            return text

        return " ".join(words[:40]) + "..."

    def _build_topics(self, segments: list[dict]) -> list[str]:
        topics = {
            segment["topic"]
            for segment in segments
            if segment.get("topic")
        }

        return sorted(topics)

    @staticmethod
    def dumps_json(data: dict | list | None) -> str | None:
        if data is None:
            return None

        return json.dumps(data, ensure_ascii=False)