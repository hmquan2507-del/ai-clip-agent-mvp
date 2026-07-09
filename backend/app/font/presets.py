from __future__ import annotations

from app.font.models import FontItem


DEFAULT_FONTS: list[FontItem] = [
    FontItem("Montserrat", "Montserrat", weight="700", language="vi", license="open_font"),
    FontItem("Poppins", "Poppins", weight="700", language="vi", license="open_font"),
    FontItem("Inter", "Inter", weight="600", language="vi", license="open_font"),
    FontItem("Roboto", "Roboto", weight="500", language="vi", license="open_font"),
    FontItem("Oswald", "Oswald", weight="700", language="vi", license="open_font"),
    FontItem("Anton", "Anton", weight="400", language="vi", license="open_font"),
    FontItem("Bebas Neue", "Bebas Neue", weight="400", language="vi", license="open_font"),
    FontItem("Noto Sans", "Noto Sans", weight="600", language="vi", license="open_font", fallback=True),
    FontItem("Noto Sans Vietnamese", "Noto Sans Vietnamese", weight="600", language="vi", license="open_font", fallback=True),
]