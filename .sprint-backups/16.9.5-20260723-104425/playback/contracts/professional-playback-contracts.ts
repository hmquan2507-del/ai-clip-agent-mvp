export type PlaybackDirection = "forward" | "reverse";
export type PlaybackStatus = "idle" | "playing" | "paused" | "stopped" | "buffering" | "ended";
export type PlaybackLoopMode = "off" | "timeline" | "in-out" | "region";
export type PlaybackCacheKind = "video" | "audio";
export type PlaybackBufferHealth = "empty" | "low" | "healthy" | "full";

export interface PlaybackRange {
  startSeconds: number;
  endSeconds: number;
}

export interface PlaybackConfiguration {
  durationSeconds: number;
  frameRate: number;
  initialTimeSeconds?: number;
  initialSpeed?: number;
  minSpeed?: number;
  maxSpeed?: number;
  followPlayhead?: boolean;
  autoScroll?: boolean;
  loopMode?: PlaybackLoopMode;
  loopRange?: PlaybackRange | null;
  cacheCapacity?: number;
  bufferTargetSeconds?: number;
  lowBufferThresholdSeconds?: number;
  syncThresholdSeconds?: number;
}

export interface PlaybackSnapshot {
  status: PlaybackStatus;
  currentTimeSeconds: number;
  durationSeconds: number;
  speed: number;
  direction: PlaybackDirection;
  loopMode: PlaybackLoopMode;
  loopRange: PlaybackRange | null;
  inPointSeconds: number | null;
  outPointSeconds: number | null;
  followPlayhead: boolean;
  autoScroll: boolean;
}

export interface PlaybackMetrics {
  renderedFrames: number;
  droppedFrames: number;
  measuredFps: number;
  averageFrameTimeMs: number;
  playbackLatencyMs: number;
  audioVideoDriftSeconds: number;
}

export interface PlaybackTick {
  nowMs: number;
  deltaMs: number;
  currentTimeSeconds: number;
  frame: number;
  status: PlaybackStatus;
}

export interface PlaybackCacheEntry<T = unknown> {
  key: string;
  kind: PlaybackCacheKind;
  frame: number;
  timeSeconds: number;
  value: T;
  sizeBytes: number;
  lastAccessedAt: number;
}

export interface PlaybackCacheStats {
  entries: number;
  bytes: number;
  hits: number;
  misses: number;
  evictions: number;
}

export interface PlaybackBufferSnapshot {
  buffered: PlaybackRange[];
  currentTimeSeconds: number;
  secondsAhead: number;
  health: PlaybackBufferHealth;
}

export interface PlaybackSyncSnapshot {
  playheadSeconds: number;
  audioSeconds: number;
  videoSeconds: number;
  driftSeconds: number;
  correctionSeconds: number;
  viewportStartSeconds: number;
  viewportEndSeconds: number;
}

export type PlaybackEvent =
  | { type: "status-changed"; status: PlaybackStatus }
  | { type: "time-changed"; timeSeconds: number; frame: number }
  | { type: "speed-changed"; speed: number }
  | { type: "direction-changed"; direction: PlaybackDirection }
  | { type: "looped"; timeSeconds: number; loopCount: number }
  | { type: "buffer-changed"; snapshot: PlaybackBufferSnapshot }
  | { type: "sync-corrected"; correctionSeconds: number }
  | { type: "metrics-changed"; metrics: PlaybackMetrics }
  | { type: "snapshot-restored"; snapshot: PlaybackSnapshot };

export interface PlaybackHistoryPort {
  record(label: string, before: PlaybackSnapshot, after: PlaybackSnapshot): void;
}

export interface PlaybackViewportPort {
  revealTime(timeSeconds: number, behavior: "instant" | "smooth"): void;
  updatePlayhead(timeSeconds: number): void;
}

export interface PlaybackMediaPort {
  play(): void | Promise<void>;
  pause(): void;
  seek(timeSeconds: number): void;
  setRate(rate: number): void;
  setMuted?(muted: boolean): void;
}

export interface PlaybackSchedulerPort {
  request(callback: (nowMs: number) => void): number;
  cancel(handle: number): void;
}
