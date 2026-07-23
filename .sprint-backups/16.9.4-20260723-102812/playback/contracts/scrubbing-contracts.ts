export const TIMELINE_SCRUBBING_CONTRACT_VERSION = "16.8.7.5" as const;

export type TimelineScrubbingStatus = "idle" | "ready" | "scrubbing" | "committing" | "cancelled" | "disposed";
export type AudioScrubbingPolicy = "muted" | "preview";

export interface TimelineScrubbingConfiguration {
  durationSeconds: number;
  fps: number;
  pixelsPerSecond?: number;
  viewportWidth?: number;
  scrollOffset?: number;
  snapToFrames?: boolean;
  previewIntervalMs?: number;
  minimumPreviewDeltaSeconds?: number;
  audioPolicy?: AudioScrubbingPolicy;
  resumePlaybackOnCommit?: boolean;
}

export interface TimelineScrubbingSnapshot {
  contractVersion: typeof TIMELINE_SCRUBBING_CONTRACT_VERSION;
  status: TimelineScrubbingStatus;
  previewTimeSeconds: number;
  committedTimeSeconds: number;
  originTimeSeconds: number;
  wasPlayingBeforeScrub: boolean;
  resumePlaybackOnCommit: boolean;
  previewFrame: number;
  pointerPixel: number | null;
  audioPolicy: AudioScrubbingPolicy;
  stateRevision: number;
  updatedAt: string | null;
}

export type TimelineScrubbingEventType = "ready" | "scrub-started" | "previewed" | "committed" | "cancelled" | "configured" | "reset";
export interface TimelineScrubbingEvent { type: TimelineScrubbingEventType; stateRevision: number; occurredAt: string; }
export type TimelineScrubbingListener = (state: TimelineScrubbingSnapshot, previous: TimelineScrubbingSnapshot, event: TimelineScrubbingEvent) => void;

export interface ScrubbingPlaybackPort {
  getSnapshot(): { currentTime: number; playing: boolean; fps: number; duration: number };
  pause(): unknown;
  seek(time: number): unknown;
  play(): unknown;
}
export interface ScrubbingPlayheadPort {
  getSnapshot(): { timeSeconds: number; isDragging: boolean; pixelsPerSecond: number; scrollOffset: number; durationSeconds: number; fps: number };
  beginDrag(): unknown;
  dragToPixel(pixel: number): { timeSeconds: number };
  moveToTime(time: number): unknown;
  endDrag(): unknown;
  cancelDrag(): unknown;
  setZoom?(value: number): unknown;
  setScrollOffset?(value: number): unknown;
  setViewport?(value: number): unknown;
}
export interface ScrubbingVideoPort { seek(time: number, source?: string): unknown; pause?(): unknown; play?(): unknown; }
export interface ScrubbingAudioPort { seek(time: number): unknown; pause?(): unknown; play?(): unknown; setMasterMuted?(value: boolean): unknown; getSnapshot?(): { masterMuted: boolean }; }
