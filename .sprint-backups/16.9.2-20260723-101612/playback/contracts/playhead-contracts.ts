export const PLAYHEAD_RUNTIME_CONTRACT_VERSION = "16.8.7.2" as const;

export type PlayheadStatus = "idle" | "ready" | "synced" | "dragging" | "disposed";

export type PlayheadEventType =
  | "ready"
  | "viewport-changed"
  | "zoom-changed"
  | "scroll-changed"
  | "moved"
  | "drag-started"
  | "drag-previewed"
  | "drag-ended"
  | "drag-cancelled"
  | "playback-synced"
  | "reset";

export interface PlayheadConfiguration {
  duration: number;
  fps: number;
  pixelsPerSecond?: number;
  viewportWidth?: number;
  scrollOffset?: number;
  initialTime?: number;
}

export interface PlayheadSnapshot {
  contractVersion: typeof PLAYHEAD_RUNTIME_CONTRACT_VERSION;
  status: PlayheadStatus;
  timeSeconds: number;
  frame: number;
  timelinePixel: number;
  viewportPixel: number;
  durationSeconds: number;
  fps: number;
  pixelsPerSecond: number;
  viewportWidth: number;
  scrollOffset: number;
  totalTimelineWidth: number;
  isDragging: boolean;
  stateRevision: number;
  updatedAt: string | null;
}

export interface PlayheadPlaybackSnapshot {
  currentTime: number;
  currentFrame?: number;
  duration?: number;
  fps?: number;
}

export interface PlayheadEvent {
  type: PlayheadEventType;
  stateRevision: number;
  occurredAt: string;
}

export type PlayheadListener = (
  state: PlayheadSnapshot,
  previous: PlayheadSnapshot,
  event: PlayheadEvent,
) => void;

export type PlayheadSeekRequester = (timeSeconds: number) => void;
