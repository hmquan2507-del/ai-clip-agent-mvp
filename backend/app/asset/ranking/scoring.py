from __future__ import annotations

from app.asset.providers.models import AssetProviderSearchResult


class AssetScoringEngine:
    PROVIDER_PRIORITY = {
        "pexels": 12.0,
        "pixabay": 10.0,
        "freesound": 8.0,
        "internal": 20.0,
        "local": 18.0,
    }

    def score(
        self,
        query: str,
        asset: AssetProviderSearchResult,
        preferred_orientation: str | None = None,
        preferred_duration: float | None = None,
    ) -> tuple[float, list[str], list[str]]:
        score = 0.0
        reasons: list[str] = []
        penalties: list[str] = []

        score += self._provider_score(asset.provider_key, reasons)
        score += self._keyword_score(query, asset, reasons)
        score += self._resolution_score(asset, reasons, penalties)
        score += self._orientation_score(asset, preferred_orientation, reasons, penalties)
        score += self._duration_score(asset, preferred_duration, reasons, penalties)

        return round(max(score, 0.0), 4), reasons, penalties

    def _provider_score(self, provider_key: str, reasons: list[str]) -> float:
        value = self.PROVIDER_PRIORITY.get(provider_key, 5.0)
        reasons.append(f"provider_priority:{provider_key}:{value}")
        return value

    def _keyword_score(
        self,
        query: str,
        asset: AssetProviderSearchResult,
        reasons: list[str],
    ) -> float:
        query_tokens = self._tokens(query)

        corpus = " ".join(
            [
                asset.title or "",
                asset.description or "",
                " ".join(asset.tags or []),
            ]
        )

        corpus_tokens = self._tokens(corpus)

        if not query_tokens or not corpus_tokens:
            return 0.0

        overlap = query_tokens.intersection(corpus_tokens)
        ratio = len(overlap) / max(len(query_tokens), 1)

        value = ratio * 35.0

        if overlap:
            reasons.append(f"keyword_overlap:{','.join(sorted(overlap))}:{round(value, 2)}")

        return value

    def _resolution_score(
        self,
        asset: AssetProviderSearchResult,
        reasons: list[str],
        penalties: list[str],
    ) -> float:
        width = asset.width or 0
        height = asset.height or 0

        if width >= 1080 and height >= 1920:
            reasons.append("high_vertical_resolution:+18")
            return 18.0

        if width >= 1920 and height >= 1080:
            reasons.append("high_landscape_resolution:+14")
            return 14.0

        if width >= 1280 and height >= 720:
            reasons.append("hd_resolution:+8")
            return 8.0

        penalties.append("low_resolution:-8")
        return -8.0

    def _orientation_score(
        self,
        asset: AssetProviderSearchResult,
        preferred_orientation: str | None,
        reasons: list[str],
        penalties: list[str],
    ) -> float:
        if not preferred_orientation:
            return 0.0

        width = asset.width or 0
        height = asset.height or 0

        if not width or not height:
            penalties.append("unknown_orientation:-2")
            return -2.0

        actual = "portrait" if height > width else "landscape"

        if actual == preferred_orientation:
            reasons.append(f"orientation_match:{actual}:+20")
            return 20.0

        penalties.append(f"orientation_mismatch:{actual}_vs_{preferred_orientation}:-12")
        return -12.0

    def _duration_score(
        self,
        asset: AssetProviderSearchResult,
        preferred_duration: float | None,
        reasons: list[str],
        penalties: list[str],
    ) -> float:
        if not preferred_duration or not asset.duration:
            return 0.0

        diff = abs(asset.duration - preferred_duration)

        if diff <= 3:
            reasons.append("duration_close:+10")
            return 10.0

        if diff <= 8:
            reasons.append("duration_acceptable:+5")
            return 5.0

        penalties.append("duration_far:-5")
        return -5.0

    def _tokens(self, text: str) -> set[str]:
        normalized = (
            text.lower()
            .replace(",", " ")
            .replace(".", " ")
            .replace("-", " ")
            .replace("_", " ")
            .replace("/", " ")
        )

        return {item.strip() for item in normalized.split() if len(item.strip()) >= 3}