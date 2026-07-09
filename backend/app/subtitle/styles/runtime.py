from __future__ import annotations

from app.subtitle.styles.models import SubtitleStyle, SubtitleStyleResolveRequest
from app.subtitle.styles.presets import DEFAULT_SUBTITLE_STYLES


class SubtitleStyleRuntime:
    def __init__(self, styles: list[SubtitleStyle] | None = None):
        self.styles = styles or DEFAULT_SUBTITLE_STYLES
        self._index = {style.key: style for style in self.styles}

    def list_styles(self) -> list[SubtitleStyle]:
        return list(self.styles)

    def get_style(self, key: str) -> SubtitleStyle | None:
        return self._index.get(key)

    def default_style(self) -> SubtitleStyle:
        return self._index["tiktok_bold"]

    def resolve_style(
        self,
        request: SubtitleStyleResolveRequest,
    ) -> SubtitleStyle:
        if request.style_key:
            style = self.get_style(request.style_key)
            if style is not None:
                return style

        if request.category:
            for style in self.styles:
                if style.category == request.category:
                    return style

        if request.platform and request.platform.lower() in {"tiktok", "reels", "shorts"}:
            return self._index["tiktok_bold"]

        if request.mood and request.mood.lower() in {"business", "corporate"}:
            return self._index["corporate"]

        if request.mood and request.mood.lower() in {"viral", "funny", "high_energy"}:
            return self._index["mrbeast"]

        return self.default_style()