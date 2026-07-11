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
        storage_roots: list[str | Path]
        | None = None,
    ):
        self.artifact_repository = (
            artifact_repository
        )

        self.storage_roots = [
            Path(item)
            for item in (
                storage_roots
                or [
                    "storage/production_render",
                    "storage/render_end_to_end_demo",
                    "storage/render_execution_integration",
                ]
            )
        ]

    def load_artifacts(
        self,
        production_id: str,
    ) -> list[Any]:
        normalized_id = (
            normalize_production_id(
                production_id
            )
        )

        repository_result = (
            call_first_supported(
                self.artifact_repository,
                self.METHOD_NAMES,
                production_id=normalized_id,
                default=None,
            )
        )

        repository_artifacts = (
            ensure_list(
                repository_result
            )
        )

        if repository_artifacts:
            first = (
                repository_artifacts[0]
            )

            if isinstance(
                first,
                dict,
            ):
                return repository_artifacts

            return (
                self._adapt_runtime_artifacts(
                    repository_artifacts
                )
            )

        manifest_artifacts = (
            self._load_manifest_artifacts(
                normalized_id
            )
        )

        if manifest_artifacts:
            return manifest_artifacts

        return (
            self._scan_artifact_directories(
                normalized_id
            )
        )

    def _adapt_runtime_artifacts(
        self,
        rows: list[Any],
    ) -> list[dict[str, Any]]:
        latest_by_key: dict[
            str,
            Any,
        ] = {}

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
            payload: dict[
                str,
                Any
            ] = {}

            raw_payload = getattr(
                row,
                "payload_json",
                None,
            )

            if isinstance(
                raw_payload,
                str,
            ) and raw_payload.strip():
                try:
                    parsed = json.loads(
                        raw_payload
                    )

                    if isinstance(
                        parsed,
                        dict,
                    ):
                        payload = parsed

                except json.JSONDecodeError:
                    payload = {}

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

            local_path = payload.get(
                "local_path",
                payload.get(
                    "path",
                ),
            )

            download_url = payload.get(
                "download_url",
                payload.get(
                    "signed_url",
                ),
            )

            file_size = payload.get(
                "file_size",
                payload.get(
                    "size",
                ),
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
                        payload.get(
                            "mime_type"
                        )
                    ),
                    "file_size": (
                        file_size
                    ),
                    "metadata": {
                        **metadata,
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
                        "checksum": (
                            getattr(
                                row,
                                "checksum",
                                None,
                            )
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
    ) -> list[Any]:
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

            artifacts = payload.get(
                "artifacts"
            )

            if isinstance(
                artifacts,
                list,
            ):
                return artifacts

        return []

    def _scan_artifact_directories(
        self,
        production_id: str,
    ) -> list[dict[str, Any]]:
        artifacts: list[
            dict[str, Any]
        ] = []

        type_map = {
            "final.mp4": "final_video",
            "preview.mp4": (
                "preview_video"
            ),
            "thumbnail.jpg": "thumbnail",
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
        }

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

            for path in (
                artifact_directory.iterdir()
            ):
                if not path.is_file():
                    continue

                artifact_type = (
                    type_map.get(
                        path.name
                    )
                )

                if artifact_type is None:
                    continue

                artifacts.append(
                    {
                        "artifact_id": (
                            artifact_type
                        ),
                        "artifact_type": (
                            artifact_type
                        ),
                        "local_path": (
                            str(path)
                        ),
                        "mime_type": (
                            mimetypes.guess_type(
                                path.name
                            )[0]
                        ),
                        "file_size": (
                            path.stat().st_size
                        ),
                        "metadata": {
                            "source": (
                                "filesystem_scan"
                            ),
                        },
                    }
                )

            if artifacts:
                break

        return artifacts