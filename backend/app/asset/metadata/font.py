from typing import Optional

from .base import BaseMetadata


class FontMetadata(BaseMetadata):
    family: Optional[str] = None
    weight: Optional[str] = None
    language: Optional[str] = None
    license: Optional[str] = None
