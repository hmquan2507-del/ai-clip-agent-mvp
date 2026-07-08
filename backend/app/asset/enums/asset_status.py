from enum import Enum


class AssetStatus(str, Enum):
    DISCOVERED = "discovered"
    DOWNLOADING = "downloading"
    READY = "ready"
    FAILED = "failed"
    DELETED = "deleted"
    EXPIRED = "expired"