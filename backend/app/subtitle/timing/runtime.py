from __future__ import annotations

import re

from app.subtitle.timing.models import (
    OptimizedSubtitleCue,
    SubtitleTimingResult,
    SubtitleTimingSegment,
)


class SubtitleTimingOptimizer:
    def __init__(
        self,
        max_words_per_cue: int = 8,
        min_duration: float = 0.8,
        max_duration: float = 2.8,
    ):
        self.max_words_per_cue = max_words_per_cue
        self.min_duration = min_duration
        self.max_duration = max_duration

    def optimize(
        self,
        production_id: str,
        segments: list[SubtitleTimingSegment],
    ) -> SubtitleTimingResult:
        cues: list[OptimizedSubtitleCue] = []

        for segment in segments:
            chunks = self._split_text(segment.text)

            if not chunks:
                continue

            segment_duration = segment.duration
            chunk_duration = segment_duration / len(chunks)

            cursor = segment.start_time

            for index, chunk in enumerate(chunks):
                duration = min(
                    self.max_duration,
                    max(self.min_duration, chunk_duration),
                )

                if index == len(chunks) - 1:
                    end_time = segment.end_time
                else:
                    end_time = min(cursor + duration, segment.end_time)

                cue_text = chunk.strip()
                word_count = len(cue_text.split())
                cps = self._characters_per_second(cue_text, cursor, end_time)

                cues.append(
                    OptimizedSubtitleCue(
                        cue_id=f"{segment.segment_id}_cue_{index + 1}",
                        segment_id=segment.segment_id,
                        start_time=round(cursor, 3),
                        end_time=round(end_time, 3),
                        text=cue_text,
                        word_count=word_count,
                        characters_per_second=cps,
                        importance_score=segment.importance_score,
                        highlight_words=self._highlight_words(cue_text, segment),
                        metadata={
                            "segment_type": segment.segment_type,
                            "source": "SubtitleTimingOptimizer",
                        },
                    )
                )

                cursor = end_time

                if cursor >= segment.end_time:
                    break

        return SubtitleTimingResult(
            production_id=production_id,
            cues=cues,
            metadata={
                "runtime": "SubtitleTimingOptimizer",
                "segment_count": len(segments),
                "cue_count": len(cues),
                "max_words_per_cue": self.max_words_per_cue,
                "min_duration": self.min_duration,
                "max_duration": self.max_duration,
            },
        )

    def _split_text(self, text: str) -> list[str]:
        text = " ".join(text.split())

        if not text:
            return []

        sentence_parts = re.split(r"(?<=[.!?。！？])\s+", text)
        chunks: list[str] = []

        for sentence in sentence_parts:
            words = sentence.split()

            for index in range(0, len(words), self.max_words_per_cue):
                chunks.append(" ".join(words[index : index + self.max_words_per_cue]))

        return chunks

    def _characters_per_second(
        self,
        text: str,
        start_time: float,
        end_time: float,
    ) -> float:
        duration = max(0.001, end_time - start_time)
        return round(len(text) / duration, 2)

    def _highlight_words(
        self,
        text: str,
        segment: SubtitleTimingSegment,
    ) -> list[str]:
        important_terms = [
            "AI",
            "video",
            "edit",
            "tự động",
            "b-roll",
            "nhạc",
            "hiệu ứng",
            "timeline",
            "upload",
        ]

        found = []

        lowered = text.lower()

        for term in important_terms:
            if term.lower() in lowered:
                found.append(term)

        if segment.segment_type in {"hook", "cta"} and not found:
            words = text.split()
            found = words[:2]

        return found