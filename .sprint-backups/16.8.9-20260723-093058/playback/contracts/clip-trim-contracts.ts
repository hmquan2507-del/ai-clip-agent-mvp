export const TIMELINE_CLIP_TRIM_CONTRACT_VERSION = "16.8.7.8" as const;

export type ClipTrimEdge = "start" | "end";
export type TimelineClipTrimStatus = "idle" | "trimming" | "committed" | "cancelled" | "disposed";
export type ClipTrimSnapTargetType = "playhead" | "clip-boundary" | "marker" | "timeline-zero" | "custom";
export type TimelineClipTrimEventType =
  | "trim_started"
  | "preview_updated"
  | "trim_committed"
  | "trim_cancelled"
  | "reset"
  | "disposed";

export interface TimelineTrimClip {
  readonly clipId: string;
  readonly trackId: string;
  readonly timelineStartFrame: number;
  readonly timelineEndFrame: number;
  readonly sourceStartFrame: number;
  readonly sourceEndFrame: number;
  readonly sourceDurationFrames: number;
}

export interface ClipTrimSnapTarget {
  readonly id: string;
  readonly frame: number;
  readonly type: ClipTrimSnapTargetType;
}

export interface TimelineClipTrimConfiguration {
  readonly framesPerSecond: number;
  readonly minimumDurationFrames?: number;
  readonly snapThresholdFrames?: number;
  readonly snapTargets?: readonly ClipTrimSnapTarget[];
}

export interface TimelineClipTrimBeginInput {
  readonly clip: TimelineTrimClip;
  readonly edge: ClipTrimEdge;
}

export interface ClipTrimPreview {
  readonly clipId: string;
  readonly trackId: string;
  readonly edge: ClipTrimEdge;
  readonly timelineStartFrame: number;
  readonly timelineEndFrame: number;
  readonly sourceStartFrame: number;
  readonly sourceEndFrame: number;
  readonly durationFrames: number;
}

export interface TimelineClipTrimCommitResult {
  readonly clipId: string;
  readonly edge: ClipTrimEdge;
  readonly deltaFrames: number;
  readonly deltaTimeSeconds: number;
  readonly snappedFrame: number | null;
  readonly snappedTargetId: string | null;
  readonly preview: ClipTrimPreview;
}

export interface TimelineClipTrimSnapshot {
  readonly contractVersion: typeof TIMELINE_CLIP_TRIM_CONTRACT_VERSION;
  readonly version: number;
  readonly status: TimelineClipTrimStatus;
  readonly clipId: string | null;
  readonly edge: ClipTrimEdge | null;
  readonly deltaFrames: number;
  readonly deltaTimeSeconds: number;
  readonly snappedFrame: number | null;
  readonly snappedTargetId: string | null;
  readonly origin: ClipTrimPreview | null;
  readonly preview: ClipTrimPreview | null;
  readonly commitResult: TimelineClipTrimCommitResult | null;
}

export interface TimelineClipTrimEvent {
  readonly type: TimelineClipTrimEventType;
  readonly snapshot: TimelineClipTrimSnapshot;
}

export type TimelineClipTrimListener = (event: TimelineClipTrimEvent) => void;
