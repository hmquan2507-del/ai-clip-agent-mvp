from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.asset.audio import AudioSearchRequest, build_audio_provider_runtime


def main() -> None:
    runtime = build_audio_provider_runtime()

    print("=== SFX Audio Search ===")
    sfx = runtime.search(
        AudioSearchRequest(
            query="whoosh transition",
            audio_type="sound_effect",
            per_page=5,
        )
    )

    for response in sfx:
        print(response.provider_key, len(response.results), response.metadata)
        print(response.results[:1])

    print("\n=== Music Audio Search ===")
    music = runtime.search(
        AudioSearchRequest(
            query="corporate background music",
            audio_type="music",
            per_page=5,
        )
    )

    for response in music:
        print(response.provider_key, len(response.results), response.metadata)
        print(response.results[:1])

    print("\nDONE: Audio provider runtime test completed.")


if __name__ == "__main__":
    main()