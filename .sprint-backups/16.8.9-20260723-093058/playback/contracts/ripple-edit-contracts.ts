export const TIMELINE_RIPPLE_EDIT_CONTRACT_VERSION = "16.8.7.9" as const;

export type RippleEditOperation = "move" | "trim-start" | "trim-end" | "delete-gap";
export type TimelineRippleStatus = "idle" | "editing" | "blocked" | "committed" | "cancelled" | "disposed";
export type RippleConflictType =
  | "locked-clip"
  | "timeline-underflow"
  | "timeline-overflow"
  | "overlap"
  | "invalid-duration"
  | "missing-anchor"
  | "invalid-gap";
export type TimelineRippleEventType =
  | "configured"
  | "ripple_started"
  | "ripple_preview_updated"
  | "ripple_blocked"
  | "ripple_committed"
  | "ripple_cancelled"
  | "reset"
  | "disposed";

export interface RippleTimelineClip {
  readonly clipId: string;
  readonly trackId: string;
  readonly timelineStartFrame: number;
  readonly timelineEndFrame: number;
  readonly sourceStartFrame: number;
  readonly sourceEndFrame: number;
  readonly locked?: boolean;
}

export interface RippleClipPosition {
  readonly clipId: string;
  readonly trackId: string;
  readonly timelineStartFrame: number;
  readonly timelineEndFrame: number;
  readonly sourceStartFrame: number;
  readonly sourceEndFrame: number;
  readonly shiftedByFrames: number;
}

export interface RippleConflict {
  readonly type: RippleConflictType;
  readonly clipId: string | null;
  readonly message: string;
}

export interface TimelineRippleConfiguration {
  readonly framesPerSecond: number;
  readonly timelineStartFrame?: number;
  readonly timelineEndFrame?: number;
  readonly affectSameTrackOnly?: boolean;
  readonly preserveRelativeSpacing?: boolean;
  readonly blockOnLockedClip?: boolean;
  readonly preventOverlap?: boolean;
}

export interface TimelineRippleBeginInput {
  readonly clips: readonly RippleTimelineClip[];
  readonly operation: Exclude<RippleEditOperation, "delete-gap">;
  readonly anchorClipId: string;
}

export interface TimelineRippleDeleteGapInput {
  readonly clips: readonly RippleTimelineClip[];
  readonly trackId: string;
  readonly gapStartFrame: number;
  readonly gapEndFrame: number;
}

export interface RippleEditCommitResult {
  readonly operation: RippleEditOperation;
  readonly anchorClipId: string | null;
  readonly trackId: string | null;
  readonly deltaFrames: number;
  readonly affectedClipIds: readonly string[];
  readonly positions: readonly RippleClipPosition[];
}

export interface TimelineRippleSnapshot {
  readonly contractVersion: typeof TIMELINE_RIPPLE_EDIT_CONTRACT_VERSION;
  readonly version: number;
  readonly status: TimelineRippleStatus;
  readonly operation: RippleEditOperation | null;
  readonly anchorClipId: string | null;
  readonly trackId: string | null;
  readonly deltaFrames: number;
  readonly affectedClipIds: readonly string[];
  readonly originPositions: readonly RippleClipPosition[];
  readonly previewPositions: readonly RippleClipPosition[];
  readonly conflicts: readonly RippleConflict[];
  readonly commitResult: RippleEditCommitResult | null;
}

export interface TimelineRippleEvent {
  readonly type: TimelineRippleEventType;
  readonly snapshot: TimelineRippleSnapshot;
}

export type TimelineRippleListener = (event: TimelineRippleEvent) => void;
