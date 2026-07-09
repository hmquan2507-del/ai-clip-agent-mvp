from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.subtitle.styles import (
    SubtitleStyleResolveRequest,
    build_subtitle_style_runtime,
)


def main() -> None:
    runtime = build_subtitle_style_runtime()

    print("=== Subtitle Styles ===")
    for style in runtime.list_styles():
        print(style.to_dict())

    print("\n=== Resolve TikTok ===")
    print(
        runtime.resolve_style(
            SubtitleStyleResolveRequest(platform="tiktok")
        ).to_dict()
    )

    print("\n=== Resolve Corporate ===")
    print(
        runtime.resolve_style(
            SubtitleStyleResolveRequest(mood="business")
        ).to_dict()
    )

    print("\nDONE: Subtitle style runtime test completed.")


if __name__ == "__main__":
    main()