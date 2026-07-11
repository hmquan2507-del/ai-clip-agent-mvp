from __future__ import annotations

from enum import StrEnum


class ProductProductionStatus(StrEnum):
    DRAFT = "draft"

    UPLOADING = "uploading"
    UPLOADED = "uploaded"

    QUEUED = "queued"

    TRANSCRIBING = "transcribing"
    ANALYZING = "analyzing"
    PLANNING = "planning"
    RESOLVING_ASSETS = "resolving_assets"
    BUILDING_TIMELINE = "building_timeline"

    RENDERING_PREVIEW = "rendering_preview"
    READY_FOR_REVIEW = "ready_for_review"

    RENDERING_FINAL = "rendering_final"
    QUALITY_CHECK = "quality_check"
    COMPLETED = "completed"

    FAILED = "failed"
    CANCELLED = "cancelled"


class ProductStage(StrEnum):
    PROJECT_SETUP = "project_setup"
    UPLOAD = "upload"
    QUEUE = "queue"

    TRANSCRIPT = "transcript"
    CONTENT_ANALYSIS = "content_analysis"
    AI_PLANNING = "ai_planning"
    ASSET_RESOLUTION = "asset_resolution"
    TIMELINE = "timeline"

    PREVIEW_RENDER = "preview_render"
    REVIEW = "review"

    FINAL_RENDER = "final_render"
    QUALITY = "quality"
    EXPORT = "export"

    FAILED = "failed"
    CANCELLED = "cancelled"


class ProductEventType(StrEnum):
    PRODUCTION_CREATED = "production_created"

    UPLOAD_STARTED = "upload_started"
    UPLOAD_PROGRESS = "upload_progress"
    UPLOAD_COMPLETED = "upload_completed"

    PIPELINE_QUEUED = "pipeline_queued"
    PIPELINE_STARTED = "pipeline_started"

    TRANSCRIPT_STARTED = "transcript_started"
    TRANSCRIPT_COMPLETED = "transcript_completed"

    ANALYSIS_STARTED = "analysis_started"
    ANALYSIS_COMPLETED = "analysis_completed"

    PLANNING_STARTED = "planning_started"
    PLANNING_COMPLETED = "planning_completed"

    ASSET_RESOLUTION_STARTED = "asset_resolution_started"
    ASSET_RESOLUTION_COMPLETED = "asset_resolution_completed"

    TIMELINE_STARTED = "timeline_started"
    TIMELINE_COMPLETED = "timeline_completed"
    TIMELINE_UPDATED = "timeline_updated"

    PREVIEW_RENDER_STARTED = "preview_render_started"
    PREVIEW_RENDER_PROGRESS = "preview_render_progress"
    PREVIEW_RENDER_COMPLETED = "preview_render_completed"

    REVIEW_READY = "review_ready"
    REVIEW_APPROVED = "review_approved"

    FINAL_RENDER_STARTED = "final_render_started"
    FINAL_RENDER_PROGRESS = "final_render_progress"
    FINAL_RENDER_COMPLETED = "final_render_completed"

    QUALITY_CHECK_STARTED = "quality_check_started"
    QUALITY_CHECK_COMPLETED = "quality_check_completed"

    EXPORT_READY = "export_ready"

    PRODUCTION_FAILED = "production_failed"
    PRODUCTION_CANCELLED = "production_cancelled"
    PRODUCTION_RETRY_STARTED = "production_retry_started"


class ProductAction(StrEnum):
    EDIT_DETAILS = "edit_details"
    START_UPLOAD = "start_upload"
    CANCEL_UPLOAD = "cancel_upload"

    RUN_AI_PIPELINE = "run_ai_pipeline"
    CANCEL_PIPELINE = "cancel_pipeline"
    RETRY_PIPELINE = "retry_pipeline"

    OPEN_REVIEW = "open_review"
    EDIT_TIMELINE = "edit_timeline"
    SAVE_TIMELINE = "save_timeline"

    RENDER_PREVIEW = "render_preview"
    RENDER_FINAL = "render_final"

    DOWNLOAD_VIDEO = "download_video"
    DOWNLOAD_SUBTITLE = "download_subtitle"
    DOWNLOAD_THUMBNAIL = "download_thumbnail"
    DOWNLOAD_TIMELINE = "download_timeline"

    DELETE_PRODUCTION = "delete_production"


class ProductErrorCode(StrEnum):
    UNKNOWN = "unknown"

    INVALID_STATE_TRANSITION = "invalid_state_transition"
    VERSION_CONFLICT = "version_conflict"

    UPLOAD_FAILED = "upload_failed"
    MEDIA_INVALID = "media_invalid"

    TRANSCRIPT_FAILED = "transcript_failed"
    ANALYSIS_FAILED = "analysis_failed"
    PLANNING_FAILED = "planning_failed"
    ASSET_RESOLUTION_FAILED = "asset_resolution_failed"
    TIMELINE_FAILED = "timeline_failed"

    PREVIEW_RENDER_FAILED = "preview_render_failed"
    FINAL_RENDER_FAILED = "final_render_failed"
    QUALITY_CHECK_FAILED = "quality_check_failed"

    ARTIFACT_MISSING = "artifact_missing"
    EXPORT_FAILED = "export_failed"