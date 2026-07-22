export const TIMELINE_CLIP_MOVE_CONTRACT_VERSION = "16.8.7.7" as const;

export type TimelineClipMoveStatus = "idle" | "moving" | "committed" | "cancelled" | "disposed";
export type TimelineClipMoveEventType =
  | "move_started"
  | "preview_updated"
  | "move_committed"
  | "move_cancelled"
  | "reset"
  | "disposed";

export interface TimelineClipMoveItem {
  readonly clipId: string;
  readonly trackId: string;
  readonly startFrame: number;
  readonly endFrame: number;
}

export interface ClipMovePreviewPosition {
  readonly clipId: string;
  readonly trackId: string;
  readonly originStartFrame: number;
  readonly originEndFrame: number;
  readonly previewStartFrame: number;
  readonly previewEndFrame: number;
}

export interface TimelineClipMoveConfiguration {
  readonly framesPerSecond: number;
  readonly durationFrames?: number;
  readonly snapThresholdFrames?: number;
  readonly snapTargets?: readonly number[];
}

export interface TimelineClipMoveBeginInput {
  readonly activeClipId: string;
  readonly clips: readonly TimelineClipMoveItem[];
}

export interface TimelineClipMoveCommitResult {
  readonly activeClipId: string;
  readonly deltaFrames: number;
  readonly deltaTimeSeconds: number;
  readonly snappedFrame: number | null;
  readonly positions: readonly ClipMovePreviewPosition[];
}

export interface TimelineClipMoveSnapshot {
  readonly contractVersion: typeof TIMELINE_CLIP_MOVE_CONTRACT_VERSION;
  readonly version: number;
  readonly status: TimelineClipMoveStatus;
  readonly selectedClipIds: readonly string[];
  readonly activeClipId: string | null;
  readonly deltaFrames: number;
  readonly deltaTimeSeconds: number;
  readonly snappedFrame: number | null;
  readonly previewPositions: readonly ClipMovePreviewPosition[];
  readonly commitResult: TimelineClipMoveCommitResult | null;
}

export interface TimelineClipMoveEvent {
  readonly type: TimelineClipMoveEventType;
  readonly snapshot: TimelineClipMoveSnapshot;
}

export type TimelineClipMoveListener = (event: TimelineClipMoveEvent) => void;
