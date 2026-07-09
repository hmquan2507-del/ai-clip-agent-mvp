from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.asset.download import AssetDownloadRequest, build_default_asset_download_runtime
from app.asset.ranking import AssetRankingRequest, build_default_asset_ranking_runtime
from app.asset.runtime import AssetRuntime
from app.asset.search import AssetSearchRequest, build_default_asset_search_runtime
from app.db.session import SessionLocal


def main() -> None:
    search_runtime = build_default_asset_search_runtime()
    ranking_runtime = build_default_asset_ranking_runtime()
    download_runtime = build_default_asset_download_runtime()

    print("=== Search Candidates ===")
    search = search_runtime.search(
        AssetSearchRequest(
            query="person editing video on laptop",
            asset_type="broll",
            per_page=3,
            orientation="portrait",
        )
    )
    print("candidates:", len(search.results))

    print("\n=== Rank Candidates ===")
    ranking = ranking_runtime.rank(
        AssetRankingRequest(
            query=search.query,
            asset_type=search.asset_type,
            candidates=search.results,
            preferred_orientation="portrait",
            preferred_duration=6,
            commercial_use=True,
            limit=1,
        )
    )

    if not ranking.ranked_assets:
        raise RuntimeError("No ranked assets available for download.")

    selected = ranking.ranked_assets[0].asset

    print("selected:", {
        "provider": selected.provider_key,
        "id": selected.provider_asset_id,
        "title": selected.title,
        "remote_url": selected.remote_url,
        "license": selected.license,
    })

    print("\n=== Download Asset ===")
    downloaded = download_runtime.download(
        AssetDownloadRequest(
            asset=selected,
            storage_root="storage/assets",
        )
    )
    print(downloaded)

    print("\n=== Save To Asset Library ===")
    db = SessionLocal()

    try:
        asset_runtime = AssetRuntime(db)
        row = asset_runtime.save_provider_asset(
            asset=selected,
            download_result=downloaded,
            status="ready",
        )

        print({
            "asset_library_id": row.id,
            "provider_key": row.provider_key,
            "provider_asset_id": row.provider_asset_id,
            "local_path": row.local_path,
            "checksum": row.checksum,
            "file_size": row.file_size,
        })

    finally:
        db.close()

    print("\nDONE: Asset download runtime test completed.")


if __name__ == "__main__":
    main()