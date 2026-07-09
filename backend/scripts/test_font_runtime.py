from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.font import FontResolveRequest, build_font_runtime


def main() -> None:
    runtime = build_font_runtime()

    print("=== Font Library ===")
    for font in runtime.list_fonts():
        print(font.to_dict())

    print("\n=== Resolve TikTok Font ===")
    print(runtime.resolve_font(FontResolveRequest(style_category="tiktok")).to_dict())

    print("\n=== Resolve Corporate Font ===")
    print(runtime.resolve_font(FontResolveRequest(style_category="corporate")).to_dict())

    print("\n=== Resolve Unknown Font ===")
    print(runtime.resolve_font(FontResolveRequest(family="Unknown Font")).to_dict())

    print("\nDONE: Font runtime test completed.")


if __name__ == "__main__":
    main()