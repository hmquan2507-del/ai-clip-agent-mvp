from __future__ import annotations


class AssetLicensePolicy:
    NON_COMMERCIAL_MARKERS = [
        "by-nc",
        "noncommercial",
        "non-commercial",
        "nc/",
    ]

    ALLOWED_COMMERCIAL_MARKERS = [
        "pexels",
        "pixabay",
        "cc0",
        "public domain",
        "royalty free",
        "royalty-free",
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

        if any(marker in normalized for marker in self.ALLOWED_COMMERCIAL_MARKERS):
            return True

        return False

    def rejection_reason(
        self,
        license_value: str | None,
    ) -> str:
        return f"license_not_allowed_for_commercial_use:{license_value or 'unknown'}"