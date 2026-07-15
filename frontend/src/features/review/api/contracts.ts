export const REVIEW_WORKSPACE_API_CONTRACT_VERSION =
  "16.2.3" as const;

export type ReviewWorkspaceAPIOperation =
  | "open_session"
  | "get_session"
  | "get_snapshot"
  | "reset_session"
  | "close_session"
  | "select_clip";

export type ReviewWorkspaceAPIErrorCode =
  | "production_not_found"
  | "workspace_load_failed"
  | "review_session_not_found"
  | "review_session_conflict"
  | "review_session_operation_failed"
  | "review_request_validation_failed"
  | "review_workspace_internal_error"
  | "http_error"
  | "invalid_response"
  | "network_error";

export type JsonPrimitive =
  | string
  | number
  | boolean
  | null;

export type JsonValue =
  | JsonPrimitive
  | JsonObject
  | JsonValue[];

export type JsonObject = {
  [key: string]: JsonValue;
};

export interface OpenReviewWorkspaceRequest {
  force_refresh?: boolean;
  replace_existing?: boolean;
}

export interface ReviewWorkspaceSessionCommandRequest {
  session_id: string;
}

export type ResetReviewWorkspaceRequest =
  ReviewWorkspaceSessionCommandRequest;

export type CloseReviewWorkspaceRequest =
  ReviewWorkspaceSessionCommandRequest;

export interface SelectTimelineClipRequest
  extends ReviewWorkspaceSessionCommandRequest {
  clip_id: string;
  additive?: boolean;
  move_cursor?: boolean;
}

export type ReviewRuntimeSessionStatus =
  | "initializing"
  | "ready"
  | "closed"
  | "error";

export interface ReviewRuntimeSessionState {
  session_id: string;
  production_id: string;
  status: ReviewRuntimeSessionStatus;
  active: boolean;
  ready: boolean;
  closed: boolean;
  timeline_revision: number;
  dirty: boolean;
  revision: number;
  created_at: string;
  updated_at: string;
  closed_at: string | null;
  error: string | null;
  metadata: JsonObject;
}

export type EditableTrackType =
  | "video_primary"
  | "video_overlay"
  | "broll"
  | "subtitle"
  | "music"
  | "sound_effect"
  | "voice"
  | "audio"
  | "effect"
  | "unknown";

export type EditableClipType =
  | "video"
  | "broll"
  | "subtitle"
  | "music"
  | "sound_effect"
  | "voice"
  | "audio"
  | "effect"
  | "unknown";

export interface EditableTimelineClip {
  clip_id: string;
  track_id: string;
  clip_type: EditableClipType;
  start_time: number;
  end_time: number;
  duration: number;
  source_start: number | null;
  source_end: number | null;
  source_duration: number | null;
  source_range_duration: number | null;
  asset_id: string | null;
  local_path: string | null;
  text: string | null;
  volume: number | null;
  opacity: number | null;
  speed: number | null;
  enabled: boolean;
  metadata: JsonObject;
}

export interface EditableTimelineTrack {
  track_id: string;
  track_type: EditableTrackType;
  name: string | null;
  position: number;
  layer: number;
  locked: boolean;
  muted: boolean;
  hidden: boolean;
  enabled: boolean;
  overlap_policy: "forbid" | "allow";
  clip_count: number;
  clips: EditableTimelineClip[];
  metadata: JsonObject;
}

export type TimelineDirtyStatus =
  | "clean"
  | "dirty"
  | "saving"
  | "saved"
  | "save_failed";

export interface EditableTimeline {
  production_id: string;
  version: string;
  duration: number;
  fps: number;
  minimum_clip_duration: number;
  width: number | null;
  height: number | null;
  track_count: number;
  clip_count: number;
  revision: number;
  dirty: boolean;
  dirty_status: TimelineDirtyStatus;
  created_at: string;
  updated_at: string;
  tracks: EditableTimelineTrack[];
  metadata: JsonObject;
}

export interface ReviewWorkspacePreview {
  available: boolean;
  video_url: string | null;
  thumbnail_url: string | null;
  duration: number;
  width: number | null;
  height: number | null;
  fps: number;
}

export interface ReviewWorkspaceTimelineSummary {
  version: string;
  duration: number;
  track_count: number;
  clip_count: number;
  tracks: EditableTimelineTrack[];
}

export interface ReviewWorkspaceView {
  production_id: string;
  version: string;

  preview: ReviewWorkspacePreview;
  timeline: ReviewWorkspaceTimelineSummary;

  review: {
    is_approved: boolean;
    notes: string | null;
  };

  export: {
    is_exported: boolean;
    export_url: string | null;
    export_format: string | null;
  };

  ai: {
    suggestions: JsonValue[];
    metadata: JsonObject;
  };

  selection: {
    selected_clip_ids: string[];
  };

  metadata: JsonObject;
}

export interface PreviewMediaSource {
  production_id: string;
  video_path: string | null;
  video_url: string | null;
  available: boolean;
  duration: number;
  width: number | null;
  height: number | null;
  fps: number;
  frame_duration: number;
  total_frames: number;
  metadata: JsonObject;
}

export interface PreviewSessionState {
  production_id: string;

  status:
    | "idle"
    | "ready"
    | "playing"
    | "paused"
    | "ended"
    | "error";

  playing: boolean;
  current_time: number;
  duration: number;
  progress: number;
  volume: number;
  muted: boolean;
  effective_volume: number;
  playback_rate: number;
  zoom: number;
  loop_enabled: boolean;
  current_frame: number;
  total_frames: number;
  revision: number;
  created_at: string;
  updated_at: string;
  error: string | null;
  metadata: JsonObject;
}

export interface PreviewTimelineSyncState {
  production_id: string;

  status:
    | "unavailable"
    | "current"
    | "stale";

  available: boolean;
  current: boolean;
  stale: boolean;
  active_timeline_revision: number;
  preview_timeline_revision: number | null;
  reason: string | null;
  updated_at: string;
  metadata: JsonObject;
}

export interface TimelineSelectableTrack {
  track_id: string;
  track_type: EditableTrackType;
  name: string | null;
  position: number;
  clip_ids: string[];
  metadata: JsonObject;
}

export interface TimelineSelectableClip {
  clip_id: string;
  track_id: string;
  clip_type: EditableClipType;
  start_time: number;
  end_time: number;
  duration: number;
  metadata: JsonObject;
}

export interface TimelineSelectionCatalog {
  production_id: string;
  duration: number;
  fps: number;
  track_count: number;
  clip_count: number;
  tracks: TimelineSelectableTrack[];
  clips: TimelineSelectableClip[];
  metadata: JsonObject;
}

export interface TimelineTimeRange {
  start_time: number;
  end_time: number;
  duration: number;
}

export interface TimelineSelectionState {
  production_id: string;

  mode:
    | "none"
    | "single"
    | "multi"
    | "range";

  focus:
    | "none"
    | "timeline"
    | "track"
    | "clip"
    | "subtitle"
    | "transition"
    | "effect"
    | "asset";

  selected_track_ids: string[];
  selected_clip_ids: string[];
  active_track_id: string | null;
  active_clip_id: string | null;
  hovered_track_id: string | null;
  hovered_clip_id: string | null;
  cursor_time: number;
  cursor_frame: number;
  selected_range: TimelineTimeRange | null;
  has_selection: boolean;
  selected_count: number;
  revision: number;
  created_at: string;
  updated_at: string;
  metadata: JsonObject;
}

export interface TimelineHistoryState {
  production_id: string;
  can_undo: boolean;
  can_redo: boolean;
  undo_count: number;
  redo_count: number;
  current_revision: number;
  maximum_history_size: number;
  next_undo_label: string | null;
  next_redo_label: string | null;
}

export interface TimelineClipboardState {
  production_id: string;

  status:
    | "empty"
    | "ready"
    | "failed";

  available: boolean;
  item_count: number;
  clip_count: number;
  clipboard_id: string;

  last_action:
    | "copy"
    | "cut"
    | "paste"
    | "clear"
    | "restore"
    | null;

  source_track_ids: string[];
}

export interface TimelineClipboardItem {
  item_id: string;
  item_type: "clip";
  source_clip_id: string;
  source_track_id: string;
  relative_start: number;
  relative_end: number;
  duration: number;
  source_order: number;
  clip: EditableTimelineClip;
  metadata: JsonObject;
}

export interface TimelineClipboardContent {
  clipboard_id: string;
  production_id: string;

  action:
    | "copy"
    | "cut"
    | "paste"
    | "clear"
    | "restore";

  status:
    | "empty"
    | "ready"
    | "failed";

  available: boolean;
  item_count: number;
  clip_count: number;
  source_track_ids: string[];
  anchor_time: number;
  total_duration: number;
  created_at: string;
  items: TimelineClipboardItem[];
  metadata: JsonObject;
}

export interface ReviewRuntimeSessionSnapshot {
  session: ReviewRuntimeSessionState;
  workspace: ReviewWorkspaceView;
  timeline: EditableTimeline;

  preview: {
    source: PreviewMediaSource;
    state: PreviewSessionState;
    sync: PreviewTimelineSyncState;
  };

  selection: {
    catalog: TimelineSelectionCatalog;
    state: TimelineSelectionState;
  };

  history: TimelineHistoryState;

  clipboard: {
    state: TimelineClipboardState;
    content: TimelineClipboardContent;
  };

  created_at: string;

  consistency: {
    production_ids_match: boolean;
    workspace_timeline_consistent: boolean;
  };

  metadata: JsonObject;
}

export interface ReviewRuntimeSessionEvent {
  event_type: string;
  session_id: string;
  production_id: string;
  session_revision: number;
  timeline_revision: number;
  created_at: string;
  metadata: JsonObject;
}

export interface ReviewWorkspaceSuccessResponseBase {
  contract_version:
    typeof REVIEW_WORKSPACE_API_CONTRACT_VERSION;

  success: true;
  operation: ReviewWorkspaceAPIOperation;
  production_id: string;
  session_id: string;
  metadata: JsonObject;
}

export interface ReviewWorkspaceSessionResponse
  extends ReviewWorkspaceSuccessResponseBase {
  operation:
    | "open_session"
    | "get_session";

  session: ReviewRuntimeSessionState;
  snapshot: ReviewRuntimeSessionSnapshot;
}

export interface ReviewWorkspaceSnapshotResponse
  extends ReviewWorkspaceSuccessResponseBase {
  operation:
    | "get_snapshot"
    | "select_clip";

  snapshot: ReviewRuntimeSessionSnapshot;
}

export interface ReviewWorkspaceResetResponse
  extends ReviewWorkspaceSuccessResponseBase {
  operation: "reset_session";
  snapshot: ReviewRuntimeSessionSnapshot;
}

export interface ReviewWorkspaceCloseResponse
  extends ReviewWorkspaceSuccessResponseBase {
  operation: "close_session";
  state: ReviewRuntimeSessionState;
  event: ReviewRuntimeSessionEvent | null;
}

export interface ReviewWorkspaceAPIErrorDetail {
  code: ReviewWorkspaceAPIErrorCode;
  message: string;
  technical_message: string | null;
  production_id: string | null;
  session_id: string | null;
  metadata: JsonObject;
}

export interface ReviewWorkspaceErrorResponse {
  contract_version:
    typeof REVIEW_WORKSPACE_API_CONTRACT_VERSION;

  success: false;
  error: ReviewWorkspaceAPIErrorDetail;
}

export type ReviewWorkspaceAPIResponse =
  | ReviewWorkspaceSessionResponse
  | ReviewWorkspaceSnapshotResponse
  | ReviewWorkspaceResetResponse
  | ReviewWorkspaceCloseResponse
  | ReviewWorkspaceErrorResponse;