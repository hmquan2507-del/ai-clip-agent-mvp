from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class VideoAssetMetadata:
    orientation: str | None = None
    camera: str | None = None
    people_count: int | None = None
    scene: str | None = None
    emotion: str | None = None
    topics: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "orientation": self.orientation,
            "camera": self.camera,
            "people_count": self.people_count,
            "scene": self.scene,
            "emotion": self.emotion,
            "topics": self.topics,
        }