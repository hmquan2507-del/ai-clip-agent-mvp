from __future__ import annotations

from typing import Any

from app.review.preview.models import (
    PreviewMediaSource,
    PreviewSessionConfig,
)
from app.review.preview.runtime import (
    PreviewEventCallback,
    PreviewSessionRuntime,
)


def build_preview_session_runtime(
    *,
    production_id: str,
    video_path: str | None = None,
    video_url: str | None = None,
    duration: float = 0.0,
    width: int | None = None,
    height: int | None = None,
    fps: float = 30.0,
    config: PreviewSessionConfig | None = None,
    event_callback: (
        PreviewEventCallback | None
    ) = None,
    metadata: dict[str, Any] | None = None,
) -> PreviewSessionRuntime:
    source = PreviewMediaSource(
        production_id=production_id,
        video_path=video_path,
        video_url=video_url,
        duration=duration,
        width=width,
        height=height,
        fps=fps,
        metadata=dict(
            metadata or {}
        ),
    )

    return PreviewSessionRuntime(
        source=source,
        config=config,
        event_callback=event_callback,
    )


def build_preview_session_from_workspace(
    workspace: Any,
    *,
    config: PreviewSessionConfig | None = None,
    event_callback: (
        PreviewEventCallback | None
    ) = None,
) -> PreviewSessionRuntime:
    production = getattr(
        workspace,
        "production",
        None,
    )

    preview = getattr(
        workspace,
        "preview",
        None,
    )

    if isinstance(
        workspace,
        dict,
    ):
        production = workspace.get(
            "production",
            {},
        )
        preview = workspace.get(
            "preview",
            {},
        )

    production_id = _read(
        production,
        "production_id",
        "",
    )

    if not production_id:
        raise ValueError(
            "Workspace does not contain "
            "production_id."
        )

    return build_preview_session_runtime(
        production_id=str(
            production_id
        ),
        video_path=_read(
            preview,
            "video_path",
        ),
        video_url=_read(
            preview,
            "video_url",
        ),
        duration=float(
            _read(
                preview,
                "duration",
                0.0,
            )
            or 0.0
        ),
        width=_read(
            preview,
            "width",
        ),
        height=_read(
            preview,
            "height",
        ),
        fps=float(
            _read(
                preview,
                "fps",
                30.0,
            )
            or 30.0
        ),
        config=config,
        event_callback=event_callback,
        metadata={
            "source": (
                "workspace_preview"
            ),
        },
    )


def _read(
    source: Any,
    key: str,
    default: Any = None,
) -> Any:
    if source is None:
        return default

    if isinstance(
        source,
        dict,
    ):
        return source.get(
            key,
            default,
        )

    return getattr(
        source,
        key,
        default,
    )