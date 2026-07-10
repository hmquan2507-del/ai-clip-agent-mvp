from __future__ import annotations

from pathlib import Path

from app.audio.beat_detection.models import (
    BeatDetectionRequest,
    BeatDetectionResult,
    BeatPoint,
    BeatSection,
)
from app.audio.beat_detection.provider import BaseBeatDetectionProvider


class MockBeatDetectionProvider(BaseBeatDetectionProvider):
    provider_key = "mock"

    def __init__(
        self,
        default_bpm: float = 120.0,
        default_duration: float = 18.0,
        beats_per_bar: int = 4,
    ):
        self.default_bpm = default_bpm
        self.default_duration = default_duration
        self.beats_per_bar = beats_per_bar

    def detect(
        self,
        request: BeatDetectionRequest,
    ) -> BeatDetectionResult:
        audio_path = Path(request.audio_path)

        if not audio_path.exists():
            raise FileNotFoundError(
                f"Audio file does not exist: {request.audio_path}"
            )

        duration = self._resolve_duration(request)
        bpm = request.expected_bpm or self.default_bpm
        beat_interval = 60.0 / bpm

        beats: list[BeatPoint] = []
        beat_time = max(0.0, request.start_time)
        beat_index = 0

        while beat_time <= duration:
            bar_position = beat_index % self.beats_per_bar
            is_downbeat = bar_position == 0
            bar_index = beat_index // self.beats_per_bar

            beats.append(
                BeatPoint(
                    beat_index=beat_index,
                    time=round(beat_time, 3),
                    strength=1.0 if is_downbeat else 0.72,
                    is_downbeat=is_downbeat,
                    bar_index=bar_index,
                    metadata={
                        "bar_position": bar_position,
                    },
                )
            )

            beat_index += 1
            beat_time += beat_interval

        sections = self._build_sections(
            beats=beats,
            duration=duration,
        )

        return BeatDetectionResult(
            audio_path=str(audio_path),
            bpm=round(bpm, 3),
            confidence=0.5,
            beats=beats,
            sections=sections,
            duration=duration,
            provider_key=self.provider_key,
            metadata={
                "beat_interval": round(beat_interval, 6),
                "beats_per_bar": self.beats_per_bar,
                "source": "deterministic_mock_provider",
            },
        )

    def _resolve_duration(
        self,
        request: BeatDetectionRequest,
    ) -> float:
        if request.end_time is not None:
            return max(request.start_time, request.end_time)

        metadata_duration = request.metadata.get("duration")

        if isinstance(metadata_duration, (int, float)):
            return max(0.0, float(metadata_duration))

        return self.default_duration

    def _build_sections(
        self,
        beats: list[BeatPoint],
        duration: float,
    ) -> list[BeatSection]:
        if not beats:
            return []

        section_duration = 4.0
        sections: list[BeatSection] = []
        cursor = 0.0
        section_index = 0

        while cursor < duration:
            end_time = min(cursor + section_duration, duration)

            section_beats = [
                beat.beat_index
                for beat in beats
                if cursor <= beat.time < end_time
            ]

            sections.append(
                BeatSection(
                    section_id=f"beat_section_{section_index + 1}",
                    start_time=round(cursor, 3),
                    end_time=round(end_time, 3),
                    section_type=self._section_type(section_index),
                    energy=self._section_energy(section_index),
                    beat_indices=section_beats,
                    metadata={
                        "source": "mock_section_generator",
                    },
                )
            )

            cursor = end_time
            section_index += 1

        return sections

    def _section_type(self, section_index: int) -> str:
        pattern = [
            "intro",
            "build",
            "peak",
            "release",
        ]

        return pattern[section_index % len(pattern)]

    def _section_energy(self, section_index: int) -> float:
        pattern = [
            0.45,
            0.65,
            0.9,
            0.55,
        ]

        return pattern[section_index % len(pattern)]