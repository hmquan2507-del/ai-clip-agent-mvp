import type {
  PlaybackDirection,
  PlaybackSessionState,
} from "./playback-contracts";
import type { VideoPreviewPort } from "./video-preview-contracts";
import type { AudioPreviewPort } from "./audio-sync-contracts";

export const PROFESSIONAL_PLAYBACK_CONTRACT_VERSION = "16.9.5" as const;

export type ProfessionalPlaybackStatus =
  | "idle"
  | "ready"
  | "playing"
  | "paused"
  | "buffering"
  | "completed"
  | "disposed";

export type ProfessionalPlaybackLoopMode =
  | "off"
  | "timeline"
  | "in-out";

export interface ProfessionalPlaybackRange {
  readonly startTime: number;
  readonly endTime: number;
}

export interface ProfessionalPlaybackConfiguration {
  readonly duration: number;
  readonly fps: number;
  readonly initialTime?: number;
  readonly initialSpeed?: number;
  readonly initialDirection?: PlaybackDirection;
  readonly initialLoopMode?: ProfessionalPlaybackLoopMode;
  readonly initialLoopRange?: ProfessionalPlaybackRange | null;
  readonly pixelsPerSecond?: number;
  readonly viewportWidth?: number;
  readonly scrollOffset?: number;
  readonly cacheCapacity?: number;
  readonly bufferTargetSeconds?: number;
  readonly lowBufferThresholdSeconds?: number;
  readonly followPlayhead?: boolean;
  readonly autoScroll?: boolean;
}

export interface ProfessionalPlaybackCacheEntry<T = unknown> {
  readonly key: string;
  readonly frame: number;
  readonly timeSeconds: number;
  readonly value: T;
  readonly sizeBytes: number;
  readonly kind: "video" | "audio";
  readonly lastAccessedAt: number;
}

export interface ProfessionalPlaybackCacheSnapshot {
  readonly entries: number;
  readonly bytes: number;
  readonly hits: number;
  readonly misses: number;
  readonly evictions: number;
}

export interface ProfessionalPlaybackBufferSnapshot {
  readonly ranges: readonly ProfessionalPlaybackRange[];
  readonly currentTime: number;
  readonly secondsAhead: number;
  readonly health: "empty" | "low" | "healthy" | "full";
}

export interface ProfessionalPlaybackMetrics {
  readonly renderedFrames: number;
  readonly droppedFrames: number;
  readonly measuredFps: number;
  readonly averageFrameTimeMs: number;
  readonly loopCount: number;
  readonly playbackLatencyMs: number;
}

export interface ProfessionalPlaybackSnapshot {
  readonly contractVersion: typeof PROFESSIONAL_PLAYBACK_CONTRACT_VERSION;
  readonly status: ProfessionalPlaybackStatus;
  readonly session: PlaybackSessionState;
  readonly loopMode: ProfessionalPlaybackLoopMode;
  readonly loopRange: ProfessionalPlaybackRange | null;
  readonly inPoint: number | null;
  readonly outPoint: number | null;
  readonly followPlayhead: boolean;
  readonly autoScroll: boolean;
  readonly buffer: ProfessionalPlaybackBufferSnapshot;
  readonly cache: ProfessionalPlaybackCacheSnapshot;
  readonly metrics: ProfessionalPlaybackMetrics;
  readonly stateRevision: number;
  readonly updatedAt: string | null;
}

export type ProfessionalPlaybackEventType =
  | "ready"
  | "played"
  | "paused"
  | "stopped"
  | "seeked"
  | "stepped"
  | "speed-changed"
  | "direction-changed"
  | "loop-changed"
  | "looped"
  | "buffer-changed"
  | "advanced"
  | "reset"
  | "disposed";

export interface ProfessionalPlaybackEvent {
  readonly type: ProfessionalPlaybackEventType;
  readonly stateRevision: number;
  readonly occurredAt: string;
}

export type ProfessionalPlaybackListener = (
  state: ProfessionalPlaybackSnapshot,
  previous: ProfessionalPlaybackSnapshot,
  event: ProfessionalPlaybackEvent,
) => void;

export interface ProfessionalPlaybackSchedulerPort {
  request(callback: (nowMs: number) => void): number;
  cancel(handle: number): void;
}

export interface ProfessionalPlaybackHistoryPort {
  record(
    label: string,
    before: ProfessionalPlaybackSnapshot,
    after: ProfessionalPlaybackSnapshot,
  ): void;
}

export interface ProfessionalPlaybackViewportPort {
  revealTime(timeSeconds: number, behavior: "instant" | "smooth"): void;
}

export interface ProfessionalPlaybackPorts {
  readonly video?: VideoPreviewPort;
  readonly audio?: ReadonlyArray<{
    descriptor: {
      readonly id: string;
      readonly kind: "voice" | "music" | "sfx";
      readonly startTimeSeconds: number;
      readonly endTimeSeconds: number;
      readonly sourceOffsetSeconds: number;
      readonly volume: number;
      readonly muted: boolean;
      readonly solo: boolean;
      readonly enabled: boolean;
    };
    port: AudioPreviewPort;
  }>;
  readonly scheduler?: ProfessionalPlaybackSchedulerPort;
  readonly history?: ProfessionalPlaybackHistoryPort;
  readonly viewport?: ProfessionalPlaybackViewportPort;
  readonly now?: () => string;
}
