import type {
  JsonObject,
  ReviewRuntimeSessionSnapshot,
} from "./contracts";

export const REVIEW_TIMELINE_COMMAND_API_CONTRACT_VERSION =
  "16.4.1" as const;

export type ReviewTimelineCommandOperation =
  | "move_clip"
  | "trim_clip_start"
  | "trim_clip_end"
  | "split_clip"
  | "duplicate_clip"
  | "delete_clip"
  | "close_gap"
  | "undo"
  | "redo";

export interface ReviewTimelineCommandRequest {
  session_id: string;
  expected_revision?: number | null;
}

export interface MoveTimelineClipRequest
  extends ReviewTimelineCommandRequest {
  clip_id: string;
  new_start_time: number;
  target_track_id?: string | null;
}

export interface TrimTimelineClipStartRequest
  extends ReviewTimelineCommandRequest {
  clip_id: string;
  new_start_time: number;
}

export interface TrimTimelineClipEndRequest
  extends ReviewTimelineCommandRequest {
  clip_id: string;
  new_end_time: number;
}

export interface SplitTimelineClipRequest
  extends ReviewTimelineCommandRequest {
  clip_id: string;
  split_time: number;
  right_clip_id?: string | null;
}

export interface DuplicateTimelineClipRequest
  extends ReviewTimelineCommandRequest {
  clip_id: string;
  new_clip_id?: string | null;
  new_start_time?: number | null;
  target_track_id?: string | null;
}

export interface DeleteTimelineClipRequest
  extends ReviewTimelineCommandRequest {
  clip_id: string;
  close_gap?: boolean;
}

export interface CloseTimelineGapRequest
  extends ReviewTimelineCommandRequest {
  track_id: string;
  gap_start: number;
  gap_end: number;
}

export type UndoTimelineCommandRequest =
  ReviewTimelineCommandRequest;

export type RedoTimelineCommandRequest =
  ReviewTimelineCommandRequest;

export interface ReviewTimelineCommandResponse {
  contract_version: typeof REVIEW_TIMELINE_COMMAND_API_CONTRACT_VERSION;
  success: true;
  operation: ReviewTimelineCommandOperation;

  production_id: string;
  session_id: string;

  snapshot: ReviewRuntimeSessionSnapshot;
  command: JsonObject | null;
  event: JsonObject | null;
  history: JsonObject;
  metadata: JsonObject;
}