from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__)
        .resolve()
        .parents[1]
    )
)

from app.review.preview import (
    PreviewPlaybackStatus,
    PreviewSessionConfig,
    build_preview_session_runtime,
)


PRODUCTION_ID = (
    "221e4b01-5fb9-4b4a-a549-4fb32c455059"
)


def main() -> None:
    captured_events = []

    runtime = (
        build_preview_session_runtime(
            production_id=PRODUCTION_ID,
            video_path=(
                "storage/"
                "render_end_to_end_demo/"
                f"{PRODUCTION_ID}/"
                "artifacts/final.mp4"
            ),
            duration=18.0,
            width=1080,
            height=1920,
            fps=30.0,
            config=(
                PreviewSessionConfig(
                    initial_volume=0.8,
                    initial_playback_rate=1.0,
                    initial_zoom=1.0,
                    loop_enabled=False,
                )
            ),
            event_callback=(
                captured_events.append
            ),
        )
    )

    print(
        "=== Preview Session Runtime ==="
    )

    print(
        "initial_status:",
        runtime.state.status.value,
    )

    play_result = runtime.play()

    print(
        "playing:",
        play_result.state.playing,
    )

    runtime.tick(2.0)

    print(
        "position_after_tick:",
        runtime.state.current_time,
    )

    runtime.seek(5.5)

    print(
        "position_after_seek:",
        runtime.state.current_time,
    )

    runtime.seek_relative(1.5)

    print(
        "position_after_relative_seek:",
        runtime.state.current_time,
    )

    runtime.set_volume(0.45)
    runtime.toggle_muted()
    runtime.set_playback_rate(1.5)
    runtime.set_zoom(1.25)
    runtime.set_loop_enabled(True)

    runtime.step_forward_frame()
    forward_frame = (
        runtime.state.current_frame
    )

    runtime.step_backward_frame()
    backward_frame = (
        runtime.state.current_frame
    )

    runtime.seek(17.5)
    runtime.play()
    runtime.tick(1.0)

    looped_position = (
        runtime.state.current_time
    )

    runtime.pause()

    snapshot_before_reset = (
        runtime.to_dict()
    )

    reset_result = runtime.reset()

    output = {
        "snapshot_before_reset": (
            snapshot_before_reset
        ),
        "reset_result": (
            reset_result.to_dict()
        ),
        "captured_event_count": len(
            captured_events
        ),
    }

    output_path = Path(
        "storage/demo_outputs/"
        "preview_session_runtime.json"
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        json.dumps(
            output,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        "volume:",
        snapshot_before_reset[
            "state"
        ]["volume"],
    )
    print(
        "muted:",
        snapshot_before_reset[
            "state"
        ]["muted"],
    )
    print(
        "playback_rate:",
        snapshot_before_reset[
            "state"
        ]["playback_rate"],
    )
    print(
        "zoom:",
        snapshot_before_reset[
            "state"
        ]["zoom"],
    )
    print(
        "loop_enabled:",
        snapshot_before_reset[
            "state"
        ]["loop_enabled"],
    )
    print(
        "forward_frame:",
        forward_frame,
    )
    print(
        "backward_frame:",
        backward_frame,
    )
    print(
        "looped_position:",
        looped_position,
    )
    print(
        "event_count:",
        len(runtime.events),
    )
    print(
        "captured_event_count:",
        len(captured_events),
    )
    print(
        "reset_status:",
        reset_result.state.status.value,
    )
    print(
        "output:",
        output_path,
    )

    assert (
        play_result.success
        is True
    )

    assert (
        snapshot_before_reset[
            "state"
        ]["volume"]
        == 0.45
    )

    assert (
        snapshot_before_reset[
            "state"
        ]["muted"]
        is True
    )

    assert (
        snapshot_before_reset[
            "state"
        ]["effective_volume"]
        == 0.0
    )

    assert (
        snapshot_before_reset[
            "state"
        ]["playback_rate"]
        == 1.5
    )

    assert (
        snapshot_before_reset[
            "state"
        ]["zoom"]
        == 1.25
    )

    assert (
        snapshot_before_reset[
            "state"
        ]["loop_enabled"]
        is True
    )

    assert (
        forward_frame
        > backward_frame
    )

    assert (
        0.0
        <= looped_position
        < 18.0
    )

    assert (
        reset_result.state.current_time
        == 0.0
    )

    assert (
        reset_result.state.status
        == PreviewPlaybackStatus.READY
    )

    assert (
        reset_result.state.volume
        == 0.8
    )

    assert (
        reset_result.state.muted
        is False
    )

    assert len(
        captured_events
    ) > 0

    print(
        "\nDONE: Preview session "
        "runtime test completed."
    )


if __name__ == "__main__":
    main()