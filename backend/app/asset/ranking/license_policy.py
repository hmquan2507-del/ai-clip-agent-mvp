from __future__ import annotations


class AssetLicensePolicy:
    NON_COMMERCIAL_MARKERS = [
        "by-nc",
        "noncommercial",
        "non-commercial",
        "/nc/",
    ]

    ALLOWED_COMMERCIAL_MARKERS = [
        "pexels",
        "pixabay",
        "cc0",
        "public domain",
        "royalty free",
        "royalty-free",
        "creativecommons.org/licenses/by/4.0",
        "creativecommons.org/licenses/by/3.0",
        "cc-by",
        "attribution",
    ]

    def is_allowed(
        self,
        license_value: str | None,
        commercial_use: bool = True,
    ) -> bool:
        if not commercial_use:
            return True

        normalized = (license_value or "").strip().lower()

        if not normalized:
            return False

        if any(marker in normalized for marker in self.NON_COMMERCIAL_MARKERS):
            return False

        return any(marker in normalized for marker in self.ALLOWED_COMMERCIAL_MARKERS)

    def requires_attribution(self, license_value: str | None) -> bool:
        normalized = (license_value or "").strip().lower()

        return (
            "creativecommons.org/licenses/by/" in normalized
            or "cc-by" in normalized
            or "attribution" in normalized
        ) and "by-nc" not in normalized

    def rejection_reason(
        self,
        license_value: str | None,
    ) -> str:
        return f"license_not_allowed_for_commercial_use:{license_value or 'unknown'}"