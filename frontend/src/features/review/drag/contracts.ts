import type {
  ReviewTimelineSnapContext,
  ReviewTimelineSnapResult,
} from "./snap-contracts";

export const REVIEW_TIMELINE_DRAG_CONTRACT_VERSION =
  "16.5.1" as const;

export const REVIEW_TIMELINE_DRAG_RUNTIME_CONTRACT_VERSION =
  "16.5.2" as const;

export type ReviewTimelineDragPhase =
  | "armed"
  | "dragging"
  | "committing"
  | "cancelled"
  | "failed";

export type ReviewTimelineDragBlockedReason =
  | "track_not_found"
  | "track_locked"
  | "incompatible_track";

export interface ReviewTimelineDragPoint {
  clientX: number;
  clientY: number;
}

export interface ReviewTimelineViewport {
  left: number;
  top: number;
  width: number;
  height: number;
  scrollLeft: number;
  contentWidth: number;
}

export interface ReviewTimelineTrackLane {
  trackId: string;
  trackType?: string;
  top: number;
  height: number;
  locked: boolean;
}

export interface ReviewTimelineDragSource {
  clipId: string;
  clipType?: string;
  trackId: string;
  startTime: number;
  endTime: number;
  duration: number;
}

export interface ReviewTimelineDragSession {
  contractVersion:
    typeof REVIEW_TIMELINE_DRAG_CONTRACT_VERSION;
  sessionId: string;
  productionId: string;
  timelineRevision: number;
  phase: ReviewTimelineDragPhase;
  source: ReviewTimelineDragSource;
  pointerOrigin: ReviewTimelineDragPoint;
  pointerCurrent: ReviewTimelineDragPoint;
  grabOffsetTime: number;
}

export interface ReviewTimelineMoveIntent {
  clipId: string;
  newStartTime: number;
  targetTrackId: string;
}

export interface ReviewTimelineDragProjection {
  source: ReviewTimelineDragSource;
  targetTrackId: string | null;
  rawStartTime: number;
  projectedStartTime: number;
  projectedEndTime: number;
  pointerInsideViewport: boolean;
  valid: boolean;
  blockedReason:
    ReviewTimelineDragBlockedReason | null;
  moveIntent:
    ReviewTimelineMoveIntent | null;
}

export interface ProjectReviewTimelineClipMoveInput {
  source: ReviewTimelineDragSource;
  pointer: ReviewTimelineDragPoint;
  grabOffsetTime: number;
  viewport: ReviewTimelineViewport;
  duration: number;
  fps: number;
  lanes: ReviewTimelineTrackLane[];
  quantizeToFrame?: boolean;
}

export type ReviewTimelineDragRuntimePhase =
  | "idle"
  | ReviewTimelineDragPhase;

export type ReviewTimelineDragCancelReason =
  | "pointer_cancelled"
  | "escape_pressed"
  | "workspace_changed"
  | "invalid_drop"
  | "disposed";

export type ReviewTimelineDragFailureCode =
  | "revision_conflict"
  | "command_rejected"
  | "unknown_error";

export interface ReviewTimelineDragFailure {
  code: ReviewTimelineDragFailureCode;
  message: string;
  technicalMessage: string | null;
  isRevisionConflict: boolean;
  expectedRevision: number | null;
  currentRevision: number | null;
}

export interface ReviewTimelineDragEnvironment {
  viewport: ReviewTimelineViewport;
  timelineDuration: number;
  fps: number;
  lanes: ReviewTimelineTrackLane[];
  quantizeToFrame?: boolean;
  snap?: ReviewTimelineSnapContext;
}

export interface ArmReviewTimelineDragInput {
  productionId: string;
  timelineRevision: number;
  source: ReviewTimelineDragSource;
  pointer: ReviewTimelineDragPoint;
  environment: ReviewTimelineDragEnvironment;
  grabOffsetTime?: number;
}

export interface MoveReviewTimelineDragInput {
  pointer: ReviewTimelineDragPoint;
  environment?: ReviewTimelineDragEnvironment;
}

export interface ReviewTimelineDragRuntimeState {
  contractVersion:
    typeof REVIEW_TIMELINE_DRAG_RUNTIME_CONTRACT_VERSION;
  phase: ReviewTimelineDragRuntimePhase;
  session: ReviewTimelineDragSession | null;
  environment:
    ReviewTimelineDragEnvironment | null;
  projection:
    ReviewTimelineDragProjection | null;
  snapResult:
    ReviewTimelineSnapResult | null;
  commitIntent:
    ReviewTimelineMoveIntent | null;
  lastCommittedIntent:
    ReviewTimelineMoveIntent | null;
  cancelReason:
    ReviewTimelineDragCancelReason | null;
  failure:
    ReviewTimelineDragFailure | null;
  lastFailure:
    ReviewTimelineDragFailure | null;
  pointerDistance: number;
  stateRevision: number;
  updatedAt: string | null;
}

export type ReviewTimelineDragRuntimeListener = (
  state: ReviewTimelineDragRuntimeState,
  previousState: ReviewTimelineDragRuntimeState,
) => void;
