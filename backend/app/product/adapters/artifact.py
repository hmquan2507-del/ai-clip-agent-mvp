from __future__ import annotations

from typing import Any

from app.product.contracts import (
    ProductArtifactSummary,
)
from app.product.adapters.models import (
    ProductPreviewSummary,
)
from app.product.adapters.utils import (
    float_or_none,
    int_or_none,
    normalize,
    read_value,
    value_of,
)


class ProductArtifactAdapter:
    def adapt_many(
        self,
        artifacts: list[Any] | None,
    ) -> list[ProductArtifactSummary]:
        return [
            self.adapt(item)
            for item in (artifacts or [])
        ]

    def adapt(
        self,
        artifact: Any,
    ) -> ProductArtifactSummary:
        metadata = normalize(
            read_value(
                artifact,
                "metadata",
                {},
            )
        )

        return ProductArtifactSummary(
            artifact_id=str(
                read_value(
                    artifact,
                    "artifact_id",
                    read_value(
                        artifact,
                        "id",
                        "",
                    ),
                )
            ),
            artifact_type=str(
                value_of(
                    read_value(
                        artifact,
                        "artifact_type",
                        "unknown",
                    )
                )
            ),
            local_path=read_value(
                artifact,
                "local_path",
            ),
            download_url=read_value(
                artifact,
                "download_url",
                read_value(
                    artifact,
                    "signed_url",
                ),
            ),
            file_size=int_or_none(
                read_value(
                    artifact,
                    "file_size",
                    read_value(
                        artifact,
                        "size",
                    ),
                )
            ),
            mime_type=read_value(
                artifact,
                "mime_type",
            ),
            metadata=metadata,
        )

    def build_preview(
        self,
        artifacts: list[Any] | None,
    ) -> ProductPreviewSummary:
        adapted = self.adapt_many(artifacts)

        final_video = self._find(
            adapted,
            {
                "final_video",
                "preview_video",
                "video",
            },
        )

        thumbnail = self._find(
            adapted,
            {
                "thumbnail",
                "preview_thumbnail",
            },
        )

        if final_video is None:
            return ProductPreviewSummary(
                available=False,
                thumbnail_path=(
                    thumbnail.local_path
                    if thumbnail
                    else None
                ),
                thumbnail_url=(
                    thumbnail.download_url
                    if thumbnail
                    else None
                ),
                metadata={
                    "adapter": "ProductArtifactAdapter",
                },
            )

        metadata = final_video.metadata

        return ProductPreviewSummary(
            available=True,
            video_path=final_video.local_path,
            video_url=final_video.download_url,
            thumbnail_path=(
                thumbnail.local_path
                if thumbnail
                else None
            ),
            thumbnail_url=(
                thumbnail.download_url
                if thumbnail
                else None
            ),
            duration=float_or_none(
                metadata.get("duration")
            ),
            width=int_or_none(
                metadata.get("width")
            ),
            height=int_or_none(
                metadata.get("height")
            ),
            fps=float_or_none(
                metadata.get("fps")
            ),
            metadata={
                "adapter": "ProductArtifactAdapter",
                "video_artifact_id": (
                    final_video.artifact_id
                ),
            },
        )

    def _find(
        self,
        artifacts: list[ProductArtifactSummary],
        artifact_types: set[str],
    ) -> ProductArtifactSummary | None:
        return next(
            (
                item
                for item in artifacts
                if item.artifact_type
                in artifact_types
            ),
            None,
        )