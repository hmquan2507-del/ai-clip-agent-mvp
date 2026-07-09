from __future__ import annotations

from app.font.models import FontItem, FontResolveRequest
from app.font.presets import DEFAULT_FONTS


class FontRuntime:
    def __init__(self, fonts: list[FontItem] | None = None):
        self.fonts = fonts or DEFAULT_FONTS
        self._index = {font.family.lower(): font for font in self.fonts}

    def list_fonts(self) -> list[FontItem]:
        return list(self.fonts)

    def get_font(self, family: str) -> FontItem | None:
        return self._index.get(family.lower())

    def fallback_font(self, language: str = "vi") -> FontItem:
        for font in self.fonts:
            if font.fallback and font.language == language:
                return font

        return self._index["noto sans"]

    def resolve_font(self, request: FontResolveRequest) -> FontItem:
        if request.family:
            font = self.get_font(request.family)
            if font is not None:
                return font

        category = (request.style_category or "").lower()

        if category in {"short_form", "tiktok", "viral"}:
            return self.get_font("Montserrat") or self.fallback_font(request.language)

        if category in {"education", "hormozi"}:
            return self.get_font("Anton") or self.fallback_font(request.language)

        if category in {"podcast", "minimal", "business", "corporate"}:
            return self.get_font("Inter") or self.fallback_font(request.language)

        if category in {"gaming", "entertainment"}:
            return self.get_font("Bebas Neue") or self.fallback_font(request.language)

        return self.fallback_font(request.language)