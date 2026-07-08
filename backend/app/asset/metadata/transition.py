from typing import Optional

from .base import BaseMetadata


class TransitionMetadata(BaseMetadata):
    transition_type: Optional[str] = None
    duration: Optional[float] = None
    direction: Optional[str] = None
