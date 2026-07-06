from __future__ import annotations

from typing import Any


class FFmpegFilterBuilder:
    def build_filters(
        self,
        render_schedule: dict[str, Any],
        resolved_assets: dict[str, Any] | None = None,
    ) -> dict[str, list[str]]:
        video_filters: list[str] = []
        audio_filters: list[str] = []

        steps = render_schedule.get("steps", [])
        if not isinstance(steps, list):
            return {
                "video": [],
                "audio": [],
            }

        for step in steps:
            if not isinstance(step, dict):
                continue

            operation = str(step.get("operation") or "")

            if operation == "apply_camera_motion":
                video_filters.append(self._zoom_filter(step))

            elif operation == "render_subtitle":
                if self._has_subtitle_asset(resolved_assets):
                    video_filters.append(self._subtitle_filter(step))

            elif operation == "render_visual_overlay":
                video_filters.append(self._overlay_filter(step))

            elif operation == "mix_audio_layer":
                if self._has_audio_asset(resolved_assets):
                    audio_filters.append(self._audio_mix_filter(step))

            elif operation == "apply_audio_ducking":
                if self._has_audio_asset(resolved_assets):
                    audio_filters.append(self._audio_ducking_filter(step))

            elif operation == "apply_audio_mastering":
                audio_filters.append(self._audio_master_filter(step))

        return {
            "video": self._deduplicate(video_filters),
            "audio": self._deduplicate(audio_filters),
        }

    def _zoom_filter(self, step: dict[str, Any]) -> str:
        params = self._params(step)
        end_scale = params.get("end_scale", 1.08)

        return f"scale=iw*{end_scale}:ih*{end_scale},crop=iw:ih"

    def _subtitle_filter(self, step: dict[str, Any]) -> str:
        return "subtitles=generated_subtitles.ass"

    def _overlay_filter(self, step: dict[str, Any]) -> str:
        return "overlay=0:0"

    def _audio_mix_filter(self, step: dict[str, Any]) -> str:
        return "amix=inputs=2:duration=first:dropout_transition=2"

    def _audio_ducking_filter(self, step: dict[str, Any]) -> str:
        return "sidechaincompress=threshold=0.05:ratio=8"

    def _audio_master_filter(self, step: dict[str, Any]) -> str:
        return "loudnorm=I=-14:TP=-1.0:LRA=11"

    def _params(self, step: dict[str, Any]) -> dict[str, Any]:
        params = step.get("parameters", {})
        return params if isinstance(params, dict) else {}

    def _deduplicate(self, filters: list[str]) -> list[str]:
        seen: set[str] = set()
        unique: list[str] = []

        for item in filters:
            if not item:
                continue

            if item in seen:
                continue

            seen.add(item)
            unique.append(item)

        return unique

    def _has_subtitle_asset(
        self,
        resolved_assets: dict[str, Any] | None,
    ) -> bool:
        if not resolved_assets:
            return False

        assets = resolved_assets.get("assets", [])
        if not isinstance(assets, list):
            return False

        return any(
            isinstance(asset, dict)
            and asset.get("asset_type") == "subtitle"
            for asset in assets
        )

    def _has_audio_asset(
        self,
        resolved_assets: dict[str, Any] | None,
    ) -> bool:
        if not resolved_assets:
            return False

        assets = resolved_assets.get("assets", [])
        if not isinstance(assets, list):
            return False

        return any(
            isinstance(asset, dict)
            and asset.get("asset_type") in {"music", "sfx", "audio"}
            and not asset.get("is_placeholder", False)
            for asset in assets
        )