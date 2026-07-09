from __future__ import annotations

from app.asset.license.models import AssetAttribution
from app.asset.providers.models import AssetProviderSearchResult
from app.asset.ranking.license_policy import AssetLicensePolicy


class AssetAttributionRuntime:
    def __init__(
        self,
        license_policy: AssetLicensePolicy | None = None,
    ):
        self.license_policy = license_policy or AssetLicensePolicy()

    def build_from_provider_asset(
        self,
        asset: AssetProviderSearchResult,
    ) -> AssetAttribution:
        metadata = asset.metadata or {}
        raw = metadata.get("raw") or {}

        author = (
            metadata.get("photographer")
            or metadata.get("username")
            or metadata.get("user")
            or raw.get("user")
            or raw.get("username")
        )

        source_url = (
            metadata.get("source_url")
            or asset.preview_url
            or asset.description
        )

        return AssetAttribution(
            provider_key=asset.provider_key,
            provider_asset_id=asset.provider_asset_id,
            title=asset.title,
            author=author,
            source_url=source_url,
            license=asset.license,
            requires_attribution=self.license_policy.requires_attribution(
                asset.license
            ),
            metadata={
                "raw_license": asset.license,
            },
        )