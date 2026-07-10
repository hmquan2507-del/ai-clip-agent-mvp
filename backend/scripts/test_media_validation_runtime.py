from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.media.validation import build_media_validation_runtime


def main() -> None:
    runtime = build_media_validation_runtime()

    valid_path = "storage/uploads/demo_source_video.mp4"
    invalid_path = "storage/uploads/empty_video.mp4"

    Path(invalid_path).touch()

    valid_result = runtime.validate(valid_path)
    invalid_result = runtime.validate(invalid_path)

    print("=== Valid Media ===")
    print(valid_result.to_dict())

    print("\n=== Invalid Media ===")
    print(invalid_result.to_dict())

    assert valid_result.valid is True
    assert valid_result.has_video is True
    assert valid_result.duration is not None
    assert valid_result.duration > 0

    assert invalid_result.valid is False
    assert "empty_file" in invalid_result.errors

    print("\nDONE: Media validation runtime test completed.")


if __name__ == "__main__":
    main()