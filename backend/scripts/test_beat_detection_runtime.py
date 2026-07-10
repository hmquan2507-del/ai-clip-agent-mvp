from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.audio.beat_detection import (
    BeatDetectionRequest,
    build_beat_detection_runtime,
)


def main() -> None:
    audio_path = Path(
        "storage/assets/music/internal_music/"
        "internal_music_corporate_background_music.mp3"
    )

    if not audio_path.exists():
        raise RuntimeError(
            f"Missing test audio file: {audio_path}"
        )

    runtime = build_beat_detection_runtime()

    result = runtime.detect(
        BeatDetectionRequest(
            audio_path=str(audio_path),
            start_time=0.0,
            end_time=18.0,
            expected_bpm=120.0,
            metadata={
                "production_id": "221e4b01-5fb9-4b4a-a549-4fb32c455059",
            },
        )
    )

    print("=== Beat Detection Result ===")
    print(result.to_dict())

    nearest = runtime.nearest_beat(
        result=result,
        target_time=4.43,
        max_distance=0.5,
    )

    print("\n=== Nearest Beat to 4.43 ===")
    print(nearest.to_dict() if nearest else None)

    downbeat = runtime.nearest_beat(
        result=result,
        target_time=10.2,
        max_distance=1.5,
        prefer_downbeat=True,
    )

    print("\n=== Nearest Downbeat to 10.2 ===")
    print(downbeat.to_dict() if downbeat else None)

    between = runtime.beats_between(
        result=result,
        start_time=4.0,
        end_time=8.0,
    )

    print("\n=== Beats Between 4 and 8 ===")
    print([beat.to_dict() for beat in between])

    print("\nDONE: Beat detection runtime test completed.")


if __name__ == "__main__":
    main()