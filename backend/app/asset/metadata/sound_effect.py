from typing import Optional

from .base import BaseMetadata


class SoundEffectMetadata(BaseMetadata):
    category: Optional[str] = None
    loudness: Optional[float] = None
    duration: Optional[float] = None
