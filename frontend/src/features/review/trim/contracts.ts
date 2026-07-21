import type {
  ReviewTimelineDragPoint,
  ReviewTimelineViewport,
} from "../drag";

export const REVIEW_TIMELINE_TRIM_CONTRACT_VERSION =
  "16.7.1" as const;

export const REVIEW_TIMELINE_TRIM_RUNTIME_CONTRACT_VERSION =
  "16.7.2" as const;

export type ReviewTimelineTrimHandle =
  | "start"
  | "end";

export type ReviewTimelineTrimBlockedReason =
  | "clip_not_editable"
  | "track_locked"
  | "range_not_trimmable"
  | "no_change";

export interface ReviewTimelineTrimSource {
  clipId: string;
  trackId: string;
  startTime: number;
  endTime: number;
  duration: number;
  editable: boolean;
  trackLocked: boolean;
}

export type ReviewTimelineTrimIntent =
  | {
      operation: "trim_clip_start";
      clipId: string;
      newStartTime: number;
    }
  | {
      operation: "trim_clip_end";
      clipId: string;
      newEndTime: number;
    };

export interface ReviewTimelineTrimProjection {
  contractVersion:
    typeof REVIEW_TIMELINE_TRIM_CONTRACT_VERSION;
  handle: ReviewTimelineTrimHandle;
  source: ReviewTimelineTrimSource;
  rawTime: number;
  projectedTime: number;
  projectedStartTime: number;
  projectedEndTime: number;
  projectedDuration: number;
  deltaTime: number;
  minimumDuration: number;
  pointerInsideViewport: boolean;
  changed: boolean;
  valid: boolean;
  blockedReason:
    ReviewTimelineTrimBlockedReason | null;
  trimIntent: ReviewTimelineTrimIntent | null;
}

export interface ProjectReviewTimelineClipTrimInput {
  handle: ReviewTimelineTrimHandle;
  source: ReviewTimelineTrimSource;
  pointer: ReviewTimelineDragPoint;
  viewport: ReviewTimelineViewport;
  timelineDuration: number;
  fps: number;
  minimumDuration?: number;
  quantizeToFrame?: boolean;
}

export interface ReviewTimelineTrimHandleGeometry {
  clipLeft: number;
  clipWidth: number;
  clientX: number;
  hitSlop?: number;
}

export type ReviewTimelineTrimPhase =
  | "armed"
  | "trimming"
  | "committing"
  | "cancelled"
  | "failed";

export type ReviewTimelineTrimRuntimePhase =
  | "idle"
  | ReviewTimelineTrimPhase;

export type ReviewTimelineTrimCancelReason =
  | "pointer_cancelled"
  | "escape_pressed"
  | "workspace_changed"
  | "invalid_projection"
  | "disposed";

export type ReviewTimelineTrimFailureCode =
  | "revision_conflict"
  | "command_rejected"
  | "unknown_error";

export interface ReviewTimelineTrimFailure {
  code: ReviewTimelineTrimFailureCode;
  message: string;
  technicalMessage: string | null;
  isRevisionConflict: boolean;
  expectedRevision: number | null;
  currentRevision: number | null;
}

export interface ReviewTimelineTrimEnvironment {
  viewport: ReviewTimelineViewport;
  timelineDuration: number;
  fps: number;
  minimumDuration?: number;
  quantizeToFrame?: boolean;
}

export interface ReviewTimelineTrimSession {
  contractVersion:
    typeof REVIEW_TIMELINE_TRIM_CONTRACT_VERSION;
  sessionId: string;
  productionId: string;
  timelineRevision: number;
  phase: ReviewTimelineTrimPhase;
  handle: ReviewTimelineTrimHandle;
  source: ReviewTimelineTrimSource;
  pointerOrigin: ReviewTimelineDragPoint;
  pointerCurrent: ReviewTimelineDragPoint;
}

export interface ArmReviewTimelineTrimInput {
  productionId: string;
  timelineRevision: number;
  handle: ReviewTimelineTrimHandle;
  source: ReviewTimelineTrimSource;
  pointer: ReviewTimelineDragPoint;
  environment: ReviewTimelineTrimEnvironment;
}

export interface MoveReviewTimelineTrimInput {
  pointer: ReviewTimelineDragPoint;
  environment?: ReviewTimelineTrimEnvironment;
}

export interface ReviewTimelineTrimRuntimeState {
  contractVersion:
    typeof REVIEW_TIMELINE_TRIM_RUNTIME_CONTRACT_VERSION;
  phase: ReviewTimelineTrimRuntimePhase;
  session: ReviewTimelineTrimSession | null;
  environment: ReviewTimelineTrimEnvironment | null;
  projection: ReviewTimelineTrimProjection | null;
  commitIntent: ReviewTimelineTrimIntent | null;
  lastCommittedIntent: ReviewTimelineTrimIntent | null;
  cancelReason: ReviewTimelineTrimCancelReason | null;
  failure: ReviewTimelineTrimFailure | null;
  lastFailure: ReviewTimelineTrimFailure | null;
  pointerDistance: number;
  stateRevision: number;
  updatedAt: string | null;
}

export type ReviewTimelineTrimRuntimeListener = (
  state: ReviewTimelineTrimRuntimeState,
  previousState: ReviewTimelineTrimRuntimeState,
) => void;
