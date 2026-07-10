from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.subtitle.timing import (
    SubtitleTimingSegment,
    build_subtitle_timing_optimizer,
)


def main() -> None:
    optimizer = build_subtitle_timing_optimizer()

    result = optimizer.optimize(
        production_id="221e4b01-5fb9-4b4a-a549-4fb32c455059",
        segments=[
            SubtitleTimingSegment(
                segment_id="seg_001",
                start_time=0,
                end_time=4,
                text="Sai lầm lớn nhất là bạn đang mất quá nhiều thời gian để edit video thủ công.",
                segment_type="hook",
                importance_score=0.9,
            ),
            SubtitleTimingSegment(
                segment_id="seg_002",
                start_time=4,
                end_time=10,
                text="AI có thể tự động hiểu nội dung và dựng video nhanh hơn.",
                segment_type="solution",
                importance_score=0.8,
            ),
            SubtitleTimingSegment(
                segment_id="seg_003",
                start_time=10,
                end_time=18,
                text="Chỉ cần upload video, AI sẽ tự tìm b-roll, nhạc, hiệu ứng và dựng timeline.",
                segment_type="cta",
                importance_score=0.85,
            ),
        ],
    )

    print("=== Subtitle Timing Optimization ===")
    print(result.to_dict())

    print("\nDONE: Subtitle timing optimizer test completed.")


if __name__ == "__main__":
    main()