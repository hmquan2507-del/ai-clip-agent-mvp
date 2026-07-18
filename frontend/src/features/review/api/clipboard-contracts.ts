import type {
  JsonObject,
  ReviewRuntimeSessionSnapshot,
  TimelineClipboardContent,
  TimelineClipboardState,
} from "./contracts";

export const REVIEW_CLIPBOARD_API_CONTRACT_VERSION =
  "16.4.8" as const;

export type ReviewClipboardOperation =
  | "copy"
  | "cut"
  | "paste"
  | "restore_history"
  | "clear_content"
  | "clear_history";

export interface ReviewClipboardCommandRequest {
  session_id: string;
  expected_revision?: number | null;
}

export interface CopyTimelineClipsRequest
  extends ReviewClipboardCommandRequest {
  clip_ids: string[];
}

export type CutTimelineClipsRequest =
  CopyTimelineClipsRequest;

export interface PasteTimelineClipsRequest
  extends ReviewClipboardCommandRequest {
  at_time: number;
  target_track_id?: string | null;
  track_mapping?: Record<string, string> | null;
}

export interface RestoreTimelineClipboardHistoryRequest
  extends ReviewClipboardCommandRequest {
  entry_id: string;
}

export type ClearTimelineClipboardRequest =
  ReviewClipboardCommandRequest;

export type ClearTimelineClipboardHistoryRequest =
  ReviewClipboardCommandRequest;

export interface TimelineClipboardHistoryState {
  entry_count: number;
  maximum_history_size: number;
  latest_entry_id: string | null;
}

export interface TimelineClipboardHistoryEntry {
  entry_id: string;
  created_at: string;
  content: TimelineClipboardContent;
  metadata: JsonObject;
}

export interface ReviewClipboardPayload {
  state: TimelineClipboardState;
  content: TimelineClipboardContent;
  event: JsonObject | null;
  history_state: TimelineClipboardHistoryState;
  history: TimelineClipboardHistoryEntry[];
}

export interface ReviewClipboardCommandResponse {
  contract_version:
    typeof REVIEW_CLIPBOARD_API_CONTRACT_VERSION;
  success: true;
  operation: ReviewClipboardOperation;
  production_id: string;
  session_id: string;
  previous_revision: number;
  current_revision: number;
  snapshot: ReviewRuntimeSessionSnapshot;
  clipboard: ReviewClipboardPayload;
  timeline_history: JsonObject | null;
  metadata: JsonObject;
}
