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
    
class EditingPlanStatus(str, Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class EditingPlanItemAction(str, Enum):
    KEEP = "keep"
    CUT = "cut"
    HOOK = "hook"
    HIGHLIGHT = "highlight"
    BROLL = "broll"
    SOUND_EFFECT = "sound_effect"
    SUBTITLE_EMPHASIS = "subtitle_emphasis"

class QueueType(str, Enum):
    TRANSCRIPT = "transcript"
    AI_EDITING = "ai_editing"
    SUBTITLE = "subtitle"
    BROLL = "broll"
    MUSIC = "music"
    THUMBNAIL = "thumbnail"
    EXPORT = "export"
    RENDER = "render"