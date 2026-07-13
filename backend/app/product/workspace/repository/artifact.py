from __future__ import annotations

import json
import mimetypes
from pathlib import Path
from typing import Any

from app.product.workspace.interfaces import (
    ArtifactWorkspaceLoader,
)
from app.product.workspace.repository.utils import (
    call_first_supported,
    ensure_list,
    normalize_production_id,
    read_json_file,
)


class RepositoryArtifactWorkspaceAdapter(
    ArtifactWorkspaceLoader
):
    METHOD_NAMES = (
        "list_by_production",
        "list_by_production_id",
        "find_by_production_id",
        "get_by_production_id",
        "list_artifacts",
        "get_artifacts",
    )

    def __init__(
        self,
        artifact_repository: Any | None = None,
        *,
        storage_roots: list[str | Path] | None = None,
    ):
        self.artifact_repository = artifact_repository

        self.storage_roots = [
            Path(item)
            for item in (
                storage_roots
                or [
                    "storage/production_render",
                    "storage/render_end_to_end_demo",
                    "storage/render_execution_integration",
                    "storage/render_quality_test",
                ]
            )
        ]

    def load_artifacts(
        self,
        production_id: str,
    ) -> list[Any]:
        normalized_id = normalize_production_id(
            production_id
        )

        repository_result = call_first_supported(
            self.artifact_repository,
            self.METHOD_NAMES,
            production_id=normalized_id,
            default=None,
        )

        repository_rows = ensure_list(
            repository_result
        )

        repository_artifacts: list[
            dict[str, Any]
        ] = []

        if repository_rows:
            if isinstance(
                repository_rows[0],
                dict,
            ):
                repository_artifacts = [
                    dict(item)
                    for item in repository_rows
                    if isinstance(item, dict)
                ]
            else:
                repository_artifacts = (
                    self._adapt_runtime_artifacts(
                        repository_rows
                    )
                )

        manifest_artifacts = (
            self._load_manifest_artifacts(
                normalized_id
            )
        )

        scanned_artifacts = (
            self._scan_artifact_directories(
                normalized_id
            )
        )

        return self._merge_artifacts(
            repository_artifacts,
            manifest_artifacts,
            scanned_artifacts,
        )

    def _adapt_runtime_artifacts(
        self,
        rows: list[Any],
    ) -> list[dict[str, Any]]:
        latest_by_key: dict[str, Any] = {}

        for row in rows:
            artifact_key = str(
                getattr(
                    row,
                    "artifact_key",
                    "",
                )
                or ""
            )

            if not artifact_key:
                continue

            current = latest_by_key.get(
                artifact_key
            )

            if current is None:
                latest_by_key[
                    artifact_key
                ] = row
                continue

            current_version = int(
                getattr(
                    current,
                    "artifact_version",
                    0,
                )
                or 0
            )

            row_version = int(
                getattr(
                    row,
                    "artifact_version",
                    0,
                )
                or 0
            )

            if row_version > current_version:
                latest_by_key[
                    artifact_key
                ] = row

        result: list[
            dict[str, Any]
        ] = []

        for artifact_key, row in (
            latest_by_key.items()
        ):
            payload = self._parse_payload_json(
                getattr(
                    row,
                    "payload_json",
                    None,
                )
            )

            artifact_type = str(
                payload.get(
                    "artifact_type",
                    artifact_key,
                )
            )

            metadata = payload.get(
                "metadata",
                {},
            )

            if not isinstance(
                metadata,
                dict,
            ):
                metadata = {}

            local_path = (
                payload.get(
                    "local_path"
                )
                or payload.get(
                    "output_path"
                )
                or payload.get(
                    "final_video_path"
                )
                or payload.get(
                    "path"
                )
            )

            download_url = (
                payload.get(
                    "download_url"
                )
                or payload.get(
                    "signed_url"
                )
            )

            file_size = payload.get(
                "file_size",
                payload.get(
                    "size",
                ),
            )

            mime_type = payload.get(
                "mime_type"
            )

            if (
                mime_type is None
                and local_path
            ):
                mime_type = (
                    mimetypes.guess_type(
                        str(local_path)
                    )[0]
                )

            result.append(
                {
                    "artifact_id": str(
                        getattr(
                            row,
                            "id",
                            artifact_key,
                        )
                    ),
                    "artifact_type": (
                        artifact_type
                    ),
                    "local_path": (
                        local_path
                    ),
                    "download_url": (
                        download_url
                    ),
                    "mime_type": (
                        mime_type
                    ),
                    "file_size": (
                        file_size
                    ),
                    "metadata": {
                        **metadata,
                        "duration": payload.get(
                            "duration",
                            payload.get(
                                "output_duration",
                            ),
                        ),
                        "width": payload.get(
                            "width",
                            payload.get(
                                "output_width",
                            ),
                        ),
                        "height": payload.get(
                            "height",
                            payload.get(
                                "output_height",
                            ),
                        ),
                        "fps": payload.get(
                            "fps",
                            payload.get(
                                "output_fps",
                            ),
                        ),
                        "video_codec": (
                            payload.get(
                                "video_codec",
                                payload.get(
                                    "output_video_codec",
                                ),
                            )
                        ),
                        "audio_codec": (
                            payload.get(
                                "audio_codec",
                                payload.get(
                                    "output_audio_codec",
                                ),
                            )
                        ),
                        "output_path": (
                            payload.get(
                                "output_path"
                            )
                        ),
                        "final_video_path": (
                            payload.get(
                                "final_video_path"
                            )
                        ),
                        "artifact_key": (
                            artifact_key
                        ),
                        "artifact_version": (
                            getattr(
                                row,
                                "artifact_version",
                                None,
                            )
                        ),
                        "checksum": getattr(
                            row,
                            "checksum",
                            None,
                        ),
                        "source": (
                            "RuntimeArtifactRepository"
                        ),
                    },
                }
            )

        return result

    def _load_manifest_artifacts(
        self,
        production_id: str,
    ) -> list[dict[str, Any]]:
        for root in self.storage_roots:
            manifest_path = (
                root
                / production_id
                / "artifacts"
                / "render_artifacts_manifest.json"
            )

            payload = read_json_file(
                manifest_path
            )

            if not isinstance(
                payload,
                dict,
            ):
                continue

            raw_artifacts = payload.get(
                "artifacts",
                [],
            )

            if not isinstance(
                raw_artifacts,
                list,
            ):
                continue

            result: list[
                dict[str, Any]
            ] = []

            for item in raw_artifacts:
                if not isinstance(
                    item,
                    dict,
                ):
                    continue

                item_metadata = item.get(
                    "metadata",
                    {},
                )

                if not isinstance(
                    item_metadata,
                    dict,
                ):
                    item_metadata = {}

                local_path = item.get(
                    "local_path"
                )

                mime_type = item.get(
                    "mime_type"
                )

                if (
                    mime_type is None
                    and local_path
                ):
                    mime_type = (
                        mimetypes.guess_type(
                            str(local_path)
                        )[0]
                    )

                result.append(
                    {
                        "artifact_id": str(
                            item.get(
                                "artifact_id",
                                item.get(
                                    "artifact_type",
                                    "",
                                ),
                            )
                        ),
                        "artifact_type": str(
                            item.get(
                                "artifact_type",
                                "unknown",
                            )
                        ),
                        "local_path": (
                            local_path
                        ),
                        "download_url": (
                            item.get(
                                "download_url"
                            )
                        ),
                        "mime_type": (
                            mime_type
                        ),
                        "file_size": (
                            item.get(
                                "file_size"
                            )
                        ),
                        "metadata": {
                            **item_metadata,
                            "duration": (
                                item.get(
                                    "duration"
                                )
                            ),
                            "width": item.get(
                                "width"
                            ),
                            "height": item.get(
                                "height"
                            ),
                            "fps": item.get(
                                "fps"
                            ),
                            "video_codec": (
                                item.get(
                                    "video_codec"
                                )
                            ),
                            "audio_codec": (
                                item.get(
                                    "audio_codec"
                                )
                            ),
                            "checksum": (
                                item.get(
                                    "checksum"
                                )
                            ),
                            "manifest_path": (
                                str(
                                    manifest_path
                                )
                            ),
                            "source": (
                                "render_artifact_manifest"
                            ),
                        },
                    }
                )

            if result:
                return result

        return []

    def _scan_artifact_directories(
        self,
        production_id: str,
    ) -> list[dict[str, Any]]:
        type_map = {
            "final.mp4": "final_video",
            "preview.mp4": "preview_video",
            "thumbnail.jpg": "thumbnail",
            "thumbnail.jpeg": "thumbnail",
            "thumbnail.png": "thumbnail",
            "render_report.json": (
                "render_report"
            ),
            "render_quality_report.json": (
                "quality_report"
            ),
            "recovery_diagnostics.json": (
                "recovery_diagnostics"
            ),
            "render_artifacts_manifest.json": (
                "artifact_manifest"
            ),
        }

        artifacts: list[
            dict[str, Any]
        ] = []

        for root in self.storage_roots:
            artifact_directory = (
                root
                / production_id
                / "artifacts"
            )

            if not (
                artifact_directory.exists()
                and artifact_directory.is_dir()
            ):
                continue

            root_artifacts: list[
                dict[str, Any]
            ] = []

            for path in sorted(
                artifact_directory.iterdir()
            ):
                if not path.is_file():
                    continue

                artifact_type = type_map.get(
                    path.name
                )

                if artifact_type is None:
                    continue

                root_artifacts.append(
                    {
                        "artifact_id": (
                            artifact_type
                        ),
                        "artifact_type": (
                            artifact_type
                        ),
                        "local_path": str(
                            path
                        ),
                        "download_url": None,
                        "mime_type": (
                            mimetypes.guess_type(
                                path.name
                            )[0]
                        ),
                        "file_size": (
                            path.stat().st_size
                        ),
                        "metadata": {
                            "filename": (
                                path.name
                            ),
                            "storage_root": (
                                str(root)
                            ),
                            "source": (
                                "filesystem_scan"
                            ),
                        },
                    }
                )

            if root_artifacts:
                artifacts.extend(
                    root_artifacts
                )

        return artifacts

    def _merge_artifacts(
        self,
        *sources: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        merged: list[
            dict[str, Any]
        ] = []

        seen: set[
            tuple[str, str, str]
        ] = set()

        for source in sources:
            for item in source:
                if not isinstance(
                    item,
                    dict,
                ):
                    continue

                artifact_type = str(
                    item.get(
                        "artifact_type",
                        "unknown",
                    )
                )

                artifact_id = str(
                    item.get(
                        "artifact_id",
                        "",
                    )
                )

                local_path = str(
                    item.get(
                        "local_path",
                        "",
                    )
                    or ""
                )

                identity = (
                    artifact_type,
                    artifact_id,
                    local_path,
                )

                if identity in seen:
                    continue

                seen.add(identity)
                merged.append(item)

        return merged

    def _parse_payload_json(
        self,
        value: Any,
    ) -> dict[str, Any]:
        if isinstance(
            value,
            dict,
        ):
            return dict(value)

        if not isinstance(
            value,
            str,
        ):
            return {}

        stripped = value.strip()

        if not stripped:
            return {}

        try:
            payload = json.loads(
                stripped
            )
        except json.JSONDecodeError:
            return {}

        if not isinstance(
            payload,
            dict,
        ):
            return {}

        return payload