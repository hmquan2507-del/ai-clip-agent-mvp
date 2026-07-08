from typing import Optional

from .base import BaseMetadata


class MotionPresetMetadata(BaseMetadata):
    zoom_type: Optional[str] = None
    strength: Optional[float] = None
    duration: Optional[float] = None
    easing: Optional[str] = None
