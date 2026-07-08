from typing import Optional

from .base import BaseMetadata


class MusicMetadata(BaseMetadata):
    genre: Optional[str] = None
    mood: Optional[str] = None
    energy: Optional[str] = None
    bpm: Optional[float] = None
    duration: Optional[float] = None
