from __future__ import annotations

from app.asset.download.runtime import AssetDownloadRuntime


def build_default_asset_download_runtime() -> AssetDownloadRuntime:
    return AssetDownloadRuntime()