from __future__ import annotations

import hashlib
import mimetypes
from pathlib import Path
from urllib.parse import urlparse

import requests

from app.asset.download.models import AssetDownloadRequest, AssetDownloadResult


class AssetDownloadRuntime:
    def download(
        self,
        request: AssetDownloadRequest,
    ) -> AssetDownloadResult:
        asset = request.asset

        if not asset.remote_url:
            raise ValueError("Asset has no remote_url to download.")

        storage_dir = Path(request.storage_root) / asset.asset_type / asset.provider_key
        storage_dir.mkdir(parents=True, exist_ok=True)

        extension = self._extension_from_url(asset.remote_url)
        filename = f"{asset.provider_key}_{asset.provider_asset_id}{extension}"
        local_path = storage_dir / filename

        response = requests.get(asset.remote_url, timeout=60)
        response.raise_for_status()

        content = response.content
        checksum = hashlib.sha256(content).hexdigest()

        local_path.write_bytes(content)

        return AssetDownloadResult(
            provider_key=asset.provider_key,
            provider_asset_id=asset.provider_asset_id,
            asset_type=asset.asset_type,
            local_path=str(local_path),
            checksum=checksum,
            file_size=len(content),
            content_type=response.headers.get("content-type"),
            metadata={
                "source_url": asset.remote_url,
                "filename": filename,
                "extension": extension,
            },
        )

    def _extension_from_url(
        self,
        url: str,
    ) -> str:
        path = urlparse(url).path
        suffix = Path(path).suffix

        if suffix:
            return suffix

        guessed = mimetypes.guess_extension(url) or ""

        return guessed or ".bin"