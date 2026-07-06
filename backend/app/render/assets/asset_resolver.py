from __future__ import annotations

from typing import Any

from app.render.assets.asset_manifest_builder import AssetManifestBuilder
from app.render.assets.models import RenderAsset, ResolvedAssets
from app.render.assets.placeholder_assets import placeholder_asset


class AssetResolver:
    def __init__(self):
        self.manifest_builder = AssetManifestBuilder()

    def resolve(
        self,
        production_id: str,
        metadata: dict[str, Any],
    ) -> ResolvedAssets:
        manifest = self.manifest_builder.build_manifest(metadata)

        assets: list[RenderAsset] = []

        assets.append(
            self._resolve_source_video(
                manifest.get("source_video", {})
            )
        )

        if manifest.get("subtitle"):
            assets.append(
                placeholder_asset(
                    asset_id="subtitle_asset",
                    asset_type="subtitle",
                    reason="subtitle_events_are_inline_in_subtitle_track",
                )
            )

        if manifest.get("broll"):
            assets.append(
                placeholder_asset(
                    asset_id="broll_asset",
                    asset_type="broll",
                    reason="broll_provider_not_integrated_yet",
                )
            )

        if manifest.get("music"):
            assets.append(
                placeholder_asset(
                    asset_id="music_asset",
                    asset_type="music",
                    reason="music_provider_not_integrated_yet",
                )
            )

        if manifest.get("sfx"):
            assets.append(
                placeholder_asset(
                    asset_id="sfx_asset",
                    asset_type="sfx",
                    reason="sfx_provider_not_integrated_yet",
                )
            )

        output_path = self._default_output_path(production_id)

        return ResolvedAssets(
            production_id=production_id,
            assets=assets,
            output_path=output_path,
            metadata={
                "resolver": "asset_resolver",
                "asset_count": len(assets),
                "manifest": manifest,
                "has_source_video": not assets[0].is_placeholder if assets else False,
            },
        )

    def _resolve_source_video(
        self,
        source_video: dict[str, Any],
    ) -> RenderAsset:
        if source_video.get("exists"):
            return RenderAsset(
                asset_id="source_video",
                asset_type="source_video",
                uri=source_video.get("uri"),
                local_path=source_video.get("local_path"),
                is_placeholder=False,
                metadata={
                    "source": "production_metadata",
                },
            )

        return placeholder_asset(
            asset_id="source_video",
            asset_type="source_video",
            reason="source_video_path_not_found_in_metadata",
        )

    def _default_output_path(self, production_id: str) -> str:
        return f"storage/renders/{production_id}/final.mp4"