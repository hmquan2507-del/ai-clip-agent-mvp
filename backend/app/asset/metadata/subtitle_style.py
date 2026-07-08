from typing import Optional

from .base import BaseMetadata


class SubtitleStyleMetadata(BaseMetadata):
    font: Optional[str] = None
    size: Optional[int] = None
    stroke: Optional[str] = None
    shadow: Optional[str] = None
    animation: Optional[str] = None
    highlight: Optional[str] = None
    position: Optional[str] = None
