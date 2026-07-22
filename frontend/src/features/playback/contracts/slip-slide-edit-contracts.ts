export const TIMELINE_SLIP_SLIDE_EDIT_CONTRACT_VERSION = "16.8.8.2" as const;

export type TimelineSlipSlideOperation = "slip" | "slide";
export type TimelineSlipSlideStatus = "idle" | "editing" | "previewing" | "blocked" | "committed" | "cancelled" | "disposed";
export type TimelineSlipSlideEventType =
  | "configured" | "slip_started" | "slide_started" | "slip_preview_updated"
  | "slide_preview_updated" | "slide_snap_applied" | "edit_blocked"
  | "edit_committed" | "edit_cancelled" | "reset" | "disposed";

export interface SlipSlideTimelineClip {
  readonly clipId: string;
  readonly trackId: string;
  readonly timelineStartFrame: number;
  readonly timelineEndFrame: number;
  readonly sourceStartFrame: number;
  readonly sourceEndFrame: number;
  readonly sourceDurationFrames: number;
  readonly locked?: boolean;
}

export interface TimelineSlipSlideConfiguration {
  readonly framesPerSecond: number;
  readonly minimumClipDurationFrames?: number;
  readonly timelineStartFrame?: number;
  readonly timelineEndFrame?: number | null;
  readonly requireContiguousNeighbors?: boolean;
  readonly blockOnLockedClip?: boolean;
  readonly clampPreviewToValidRange?: boolean;
  readonly magneticSnapEnabled?: boolean;
}

export type SlipSlideConflictCode =
  | "missing-active-clip" | "missing-previous-clip" | "missing-next-clip"
  | "track-mismatch" | "non-contiguous-neighbors" | "locked-active-clip"
  | "locked-previous-clip" | "locked-next-clip" | "invalid-timeline-range"
  | "invalid-source-range" | "source-underflow" | "source-overflow"
  | "timeline-underflow" | "timeline-overflow" | "minimum-duration-violation"
  | "overlap-detected" | "gap-detected" | "invalid-delta";

export interface SlipSlideConflict {
  readonly code: SlipSlideConflictCode;
  readonly message: string;
  readonly clipId?: string | null;
  readonly requestedDeltaFrames?: number | null;
  readonly allowedDeltaFrames?: number | null;
  readonly blocking: boolean;
}

export interface SlipSlideClipPosition {
  readonly clipId: string;
  readonly trackId: string;
  readonly timelineStartFrame: number;
  readonly timelineEndFrame: number;
  readonly sourceStartFrame: number;
  readonly sourceEndFrame: number;
}

export interface TimelineSlipPreview {
  readonly operation: "slip";
  readonly requestedDeltaFrames: number;
  readonly resolvedDeltaFrames: number;
  readonly original: SlipSlideClipPosition;
  readonly preview: SlipSlideClipPosition;
  readonly minimumDeltaFrames: number;
  readonly maximumDeltaFrames: number;
  readonly clamped: boolean;
  readonly blocked: boolean;
  readonly conflicts: readonly SlipSlideConflict[];
}

export interface TimelineSlidePreview {
  readonly operation: "slide";
  readonly requestedDeltaFrames: number;
  readonly resolvedDeltaFrames: number;
  readonly previousOriginal: SlipSlideClipPosition;
  readonly activeOriginal: SlipSlideClipPosition;
  readonly nextOriginal: SlipSlideClipPosition;
  readonly previousPreview: SlipSlideClipPosition;
  readonly activePreview: SlipSlideClipPosition;
  readonly nextPreview: SlipSlideClipPosition;
  readonly minimumDeltaFrames: number;
  readonly maximumDeltaFrames: number;
  readonly clamped: boolean;
  readonly blocked: boolean;
  readonly conflicts: readonly SlipSlideConflict[];
  readonly snapped: boolean;
  readonly snapTargetId: string | null;
  readonly snapTargetFrame: number | null;
}

export interface TimelineSlipSlideSession {
  readonly sessionId: string;
  readonly operation: TimelineSlipSlideOperation;
  readonly activeClipId: string;
  readonly previousClipId: string | null;
  readonly nextClipId: string | null;
  readonly startedAtVersion: number;
}

export interface BeginTimelineSlipRequest {
  readonly sessionId: string;
  readonly clip: SlipSlideTimelineClip;
}

export interface BeginTimelineSlideRequest {
  readonly sessionId: string;
  readonly previousClip: SlipSlideTimelineClip | null;
  readonly activeClip: SlipSlideTimelineClip;
  readonly nextClip: SlipSlideTimelineClip | null;
}

export interface SlipSlideSnapResolver {
  resolveSlideDelta(request: {
    readonly activeClip: SlipSlideTimelineClip;
    readonly requestedDeltaFrames: number;
    readonly excludedOwnerIds: readonly string[];
  }): {
    readonly resolvedDeltaFrames: number;
    readonly snapped: boolean;
    readonly targetId: string | null;
    readonly targetFrame: number | null;
  };
}

export interface PreviewSlideWithSnapRequest {
  readonly deltaFrames: number;
  readonly resolver: SlipSlideSnapResolver;
}

export interface TimelineSlipSlideCommitResult {
  readonly sessionId: string;
  readonly operation: TimelineSlipSlideOperation;
  readonly committed: boolean;
  readonly positions: readonly SlipSlideClipPosition[];
  readonly requestedDeltaFrames: number;
  readonly resolvedDeltaFrames: number;
  readonly conflicts: readonly SlipSlideConflict[];
}

export interface TimelineSlipSlideSnapshot {
  readonly contractVersion: typeof TIMELINE_SLIP_SLIDE_EDIT_CONTRACT_VERSION;
  readonly version: number;
  readonly status: TimelineSlipSlideStatus;
  readonly configured: boolean;
  readonly session: TimelineSlipSlideSession | null;
  readonly slipPreview: TimelineSlipPreview | null;
  readonly slidePreview: TimelineSlidePreview | null;
  readonly lastCommit: TimelineSlipSlideCommitResult | null;
  readonly conflicts: readonly SlipSlideConflict[];
}

export interface TimelineSlipSlideEvent {
  readonly type: TimelineSlipSlideEventType;
  readonly snapshot: TimelineSlipSlideSnapshot;
}
export type TimelineSlipSlideListener = (event: TimelineSlipSlideEvent) => void;
