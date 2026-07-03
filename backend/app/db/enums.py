from enum import Enum


class ProductionStatus(str, Enum):
    DRAFT = "draft"
    UPLOADED = "uploaded"
    QUEUED = "queued"
    PROCESSING = "processing"
    REVIEW_READY = "review_ready"
    APPROVED = "approved"
    RENDERING = "rendering"
    EXPORTED = "exported"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AssetType(str, Enum):
    SOURCE_VIDEO = "source_video"
    TRANSCRIPT = "transcript"
    SUBTITLE = "subtitle"
    PREVIEW = "preview"
    EXPORT = "export"


class ClipStatus(str, Enum):
    DRAFT = "draft"
    SELECTED = "selected"
    REJECTED = "rejected"
    APPROVED = "approved"
    FAILED = "failed"


class RenderJobStatus(str, Enum):
    QUEUED = "queued"
    RENDERING = "rendering"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExportStatus(str, Enum):
    QUEUED = "queued"
    RENDERING = "rendering"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"

class UploadStatus(str, Enum):
    PENDING = "pending"
    VALIDATING = "validating"
    STORED = "stored"
    ATTACHED = "attached"
    FAILED = "failed"



class QueueStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class QueueType(str, Enum):
    TRANSCRIPT = "transcript"
    SUBTITLE = "subtitle"
    BROLL = "broll"
    MUSIC = "music"
    THUMBNAIL = "thumbnail"
    EXPORT = "export"
    RENDER = "render"