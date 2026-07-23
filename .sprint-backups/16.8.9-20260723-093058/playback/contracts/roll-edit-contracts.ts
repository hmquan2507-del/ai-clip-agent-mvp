export const TIMELINE_ROLL_EDIT_CONTRACT_VERSION = "16.8.8.3" as const;

export type TimelineRollEditStatus = "idle" | "editing" | "previewing" | "blocked" | "committed" | "cancelled" | "disposed";
export type TimelineRollEditEventType =
  | "configured" | "snap_resolver_set" | "snap_resolver_cleared" | "roll_started"
  | "roll_preview_updated" | "roll_snap_applied" | "roll_blocked" | "roll_committed"
  | "roll_cancelled" | "reset" | "disposed";

export interface RollTimelineClip {
  readonly clipId: string;
  readonly trackId: string;
  readonly timelineStartFrame: number;
  readonly timelineEndFrame: number;
  readonly sourceStartFrame: number;
  readonly sourceEndFrame: number;
  readonly sourceDurationFrames: number;
  readonly locked?: boolean;
}

export interface TimelineRollEditConfiguration {
  readonly framesPerSecond: number;
  readonly minimumClipDurationFrames?: number;
  readonly timelineStartFrame?: number;
  readonly timelineEndFrame?: number | null;
  readonly requireContiguousClips?: boolean;
  readonly blockOnLockedClip?: boolean;
  readonly clampPreviewToValidRange?: boolean;
  readonly magneticSnapEnabled?: boolean;
}

export type TimelineRollConflictCode =
  | "missing-left-clip" | "missing-right-clip" | "track-mismatch" | "non-contiguous-clips"
  | "locked-left-clip" | "locked-right-clip" | "invalid-left-timeline-range"
  | "invalid-right-timeline-range" | "invalid-left-source-range" | "invalid-right-source-range"
  | "duration-mismatch" | "left-minimum-duration-violation" | "right-minimum-duration-violation"
  | "left-source-overflow" | "right-source-underflow" | "timeline-underflow" | "timeline-overflow"
  | "gap-detected" | "overlap-detected" | "invalid-delta" | "invalid-roll-range";

export interface TimelineRollConflict {
  readonly code: TimelineRollConflictCode;
  readonly message: string;
  readonly clipId?: string | null;
  readonly requestedDeltaFrames?: number | null;
  readonly allowedDeltaFrames?: number | null;
  readonly blocking: boolean;
}

export interface RollClipPosition {
  readonly clipId: string;
  readonly trackId: string;
  readonly timelineStartFrame: number;
  readonly timelineEndFrame: number;
  readonly sourceStartFrame: number;
  readonly sourceEndFrame: number;
}

export interface TimelineRollPreview {
  readonly requestedDeltaFrames: number;
  readonly resolvedDeltaFrames: number;
  readonly originalCutFrame: number;
  readonly previewCutFrame: number;
  readonly leftOriginal: RollClipPosition;
  readonly rightOriginal: RollClipPosition;
  readonly leftPreview: RollClipPosition;
  readonly rightPreview: RollClipPosition;
  readonly minimumDeltaFrames: number;
  readonly maximumDeltaFrames: number;
  readonly snapped: boolean;
  readonly snapTargetId: string | null;
  readonly snapTargetFrame: number | null;
  readonly clamped: boolean;
  readonly blocked: boolean;
  readonly conflicts: readonly TimelineRollConflict[];
}

export interface TimelineRollEditSession {
  readonly sessionId: string;
  readonly leftClipId: string;
  readonly rightClipId: string;
  readonly trackId: string;
  readonly originalCutFrame: number;
  readonly startedAtVersion: number;
}

export interface BeginTimelineRollEditRequest {
  readonly sessionId: string;
  readonly leftClip: RollTimelineClip | null;
  readonly rightClip: RollTimelineClip | null;
}

export interface TimelineRollSnapResolver {
  resolveRollCut(request: {
    readonly originalCutFrame: number;
    readonly proposedCutFrame: number;
    readonly leftClip: RollTimelineClip;
    readonly rightClip: RollTimelineClip;
    readonly excludedOwnerIds: readonly string[];
  }): {
    readonly resolvedCutFrame: number;
    readonly snapped: boolean;
    readonly targetId: string | null;
    readonly targetFrame: number | null;
  };
}

export interface TimelineRollCommitResult {
  readonly sessionId: string;
  readonly committed: boolean;
  readonly originalCutFrame: number;
  readonly committedCutFrame: number;
  readonly requestedDeltaFrames: number;
  readonly resolvedDeltaFrames: number;
  readonly positions: readonly [RollClipPosition, RollClipPosition];
  readonly conflicts: readonly TimelineRollConflict[];
}

export interface TimelineRollEditSnapshot {
  readonly contractVersion: typeof TIMELINE_ROLL_EDIT_CONTRACT_VERSION;
  readonly version: number;
  readonly status: TimelineRollEditStatus;
  readonly configured: boolean;
  readonly session: TimelineRollEditSession | null;
  readonly preview: TimelineRollPreview | null;
  readonly lastCommit: TimelineRollCommitResult | null;
  readonly conflicts: readonly TimelineRollConflict[];
}

export interface TimelineRollEditEvent {
  readonly type: TimelineRollEditEventType;
  readonly snapshot: TimelineRollEditSnapshot;
}
export type TimelineRollEditListener = (event: TimelineRollEditEvent) => void;
