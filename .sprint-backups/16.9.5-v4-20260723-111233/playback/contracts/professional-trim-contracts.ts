export const PROFESSIONAL_TRIM_CONTRACT_VERSION = "16.9.1" as const;

export type ProfessionalTrimMode = "ripple-start" | "ripple-end" | "roll" | "slip" | "slide";
export type ProfessionalTrimStatus = "idle" | "editing" | "blocked" | "committed" | "cancelled" | "disposed";

export interface ProfessionalTrimClip {
  readonly clipId: string;
  readonly trackId: string;
  readonly timelineStartFrame: number;
  readonly timelineEndFrame: number;
  readonly sourceStartFrame: number;
  readonly sourceEndFrame: number;
  readonly sourceDurationFrames: number;
  readonly locked?: boolean;
}

export interface ProfessionalTrimConfiguration {
  readonly framesPerSecond: number;
  readonly minimumDurationFrames?: number;
  readonly timelineStartFrame?: number;
  readonly timelineEndFrame?: number | null;
  readonly magneticTimeline?: boolean;
  readonly autoCloseGaps?: boolean;
  readonly blockOnLockedClip?: boolean;
}

export interface ProfessionalTrimBeginRequest {
  readonly sessionId: string;
  readonly mode: ProfessionalTrimMode;
  readonly clips: readonly ProfessionalTrimClip[];
  readonly activeClipId: string;
  readonly secondaryClipId?: string | null;
}

export interface ProfessionalTrimPosition extends ProfessionalTrimClip {
  readonly shiftedByFrames: number;
}

export interface TimelineGap {
  readonly gapId: string;
  readonly trackId: string;
  readonly startFrame: number;
  readonly endFrame: number;
  readonly durationFrames: number;
  readonly previousClipId: string | null;
  readonly nextClipId: string | null;
}

export interface ProfessionalTrimConflict {
  readonly code: "missing-clip" | "locked-clip" | "invalid-neighbor" | "minimum-duration" | "source-underflow" | "source-overflow" | "timeline-underflow" | "timeline-overflow" | "overlap";
  readonly message: string;
  readonly clipId?: string | null;
  readonly blocking: boolean;
}

export interface ProfessionalTrimPreview {
  readonly requestedDeltaFrames: number;
  readonly resolvedDeltaFrames: number;
  readonly positions: readonly ProfessionalTrimPosition[];
  readonly gaps: readonly TimelineGap[];
  readonly conflicts: readonly ProfessionalTrimConflict[];
  readonly blocked: boolean;
}

export interface ProfessionalTrimCommitResult {
  readonly sessionId: string;
  readonly mode: ProfessionalTrimMode;
  readonly positions: readonly ProfessionalTrimPosition[];
  readonly affectedClipIds: readonly string[];
  readonly resolvedDeltaFrames: number;
  readonly autoClosedGapIds: readonly string[];
}

export interface ProfessionalTrimSnapshot {
  readonly contractVersion: typeof PROFESSIONAL_TRIM_CONTRACT_VERSION;
  readonly version: number;
  readonly status: ProfessionalTrimStatus;
  readonly sessionId: string | null;
  readonly mode: ProfessionalTrimMode | null;
  readonly activeClipId: string | null;
  readonly secondaryClipId: string | null;
  readonly origin: readonly ProfessionalTrimPosition[];
  readonly preview: ProfessionalTrimPreview | null;
  readonly lastCommit: ProfessionalTrimCommitResult | null;
}

export interface ProfessionalTrimHistoryPort {
  commitTrim(input: {
    readonly label: string;
    readonly before: readonly ProfessionalTrimPosition[];
    readonly after: readonly ProfessionalTrimPosition[];
    readonly affectedClipIds: readonly string[];
  }): void | Promise<void>;
}

export type ProfessionalTrimListener = (snapshot: ProfessionalTrimSnapshot) => void;
