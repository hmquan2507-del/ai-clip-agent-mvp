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
    TIMELINE = "timeline"
    SUBTITLE_RUNTIME = "subtitle_runtime"
    BROLL_RUNTIME = "broll_runtime"
    SOUND_EFFECT_RUNTIME = "sound_effect_runtime"
    MUSIC_RUNTIME = "music_runtime"
    RENDER_RUNTIME = "render_runtime"

class TimelineStatus(str, Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TimelineTrackType(str, Enum):
    VIDEO = "video"
    AUDIO = "audio"
    SUBTITLE = "subtitle"
    BROLL = "broll"
    SOUND_EFFECT = "sound_effect"
    MUSIC = "music"


class TimelineClipType(str, Enum):
    SOURCE = "source"
    GENERATED = "generated"
    SUBTITLE = "subtitle"
    BROLL = "broll"
    SOUND_EFFECT = "sound_effect"
    MUSIC = "music"

class SubtitleStatus(str, Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class SubtitleStyle(str, Enum):
    DEFAULT = "default"
    BOLD_KEYWORD = "bold_keyword"
    TIKTOK = "tiktok"
    MINIMAL = "minimal"

class BrollStatus(str, Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class BrollSourceType(str, Enum):
    SUGGESTION = "suggestion"
    STOCK = "stock"
    GENERATED = "generated"
    UPLOADED = "uploaded"
    
class SoundEffectStatus(str, Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class SoundEffectType(str, Enum):
    WHOOSH = "whoosh"
    POP = "pop"
    CLICK = "click"
    TRANSITION = "transition"
    IMPACT = "impact"
    AMBIENT = "ambient"
    CUSTOM = "custom"

class MusicStatus(str, Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class MusicMood(str, Enum):
    ENERGETIC = "energetic"
    CALM = "calm"
    CINEMATIC = "cinematic"
    CORPORATE = "corporate"
    INSPIRATIONAL = "inspirational"
    MINIMAL = "minimal"
    CUSTOM = "custom"

class RenderPlanStatus(str, Enum):
    DRAFT = "draft"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class RenderTrackType(str, Enum):
    VIDEO = "video"
    SUBTITLE = "subtitle"
    BROLL = "broll"
    SOUND_EFFECT = "sound_effect"
    MUSIC = "music"
    EXPORT = "export"


class RenderAssetType(str, Enum):
    SOURCE_VIDEO = "source_video"
    SUBTITLE = "subtitle"
    BROLL = "broll"
    SOUND_EFFECT = "sound_effect"
    MUSIC = "music"
    GENERATED = "generated"