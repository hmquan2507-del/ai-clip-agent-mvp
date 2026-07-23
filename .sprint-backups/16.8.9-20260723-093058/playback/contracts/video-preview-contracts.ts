export const VIDEO_PREVIEW_CONTRACT_VERSION = "16.8.7.3" as const;

export type VideoPreviewStatus =
  | "detached"
  | "loading"
  | "ready"
  | "playing"
  | "paused"
  | "seeking"
  | "buffering"
  | "ended"
  | "error"
  | "disposed";

export type VideoPreviewEventName =
  | "loadedmetadata"
  | "timeupdate"
  | "seeking"
  | "seeked"
  | "ended"
  | "waiting"
  | "playing"
  | "pause"
  | "error";

export type VideoPreviewSyncSource =
  | "playback-command"
  | "media-event"
  | "playhead-drag"
  | "internal-correction";

export interface VideoPreviewPort {
  readonly currentTime: number;
  readonly duration: number;
  readonly paused: boolean;
  readonly seeking: boolean;
  readonly ended: boolean;
  readonly playbackRate: number;
  play(): Promise<void>;
  pause(): void;
  setCurrentTime(value: number): void;
  setPlaybackRate(value: number): void;
  subscribe(event: VideoPreviewEventName, listener: () => void): () => void;
}

export interface VideoPreviewConfiguration {
  fps: number;
  driftThreshold?: number;
  largeDriftThreshold?: number;
}

export interface VideoPreviewSnapshot {
  contractVersion: typeof VIDEO_PREVIEW_CONTRACT_VERSION;
  status: VideoPreviewStatus;
  attached: boolean;
  currentTimeSeconds: number;
  durationSeconds: number;
  playbackRate: number;
  paused: boolean;
  seeking: boolean;
  buffering: boolean;
  ended: boolean;
  driftSeconds: number;
  lastSource: VideoPreviewSyncSource | null;
  errorMessage: string | null;
  stateRevision: number;
  updatedAt: string | null;
}

export type VideoPreviewEventType =
  | "attached"
  | "detached"
  | "metadata-synced"
  | "play-synced"
  | "pause-synced"
  | "stop-synced"
  | "seek-synced"
  | "rate-synced"
  | "media-time-synced"
  | "buffering-started"
  | "buffering-ended"
  | "media-ended"
  | "error"
  | "reset";

export interface VideoPreviewEvent {
  type: VideoPreviewEventType;
  stateRevision: number;
  occurredAt: string;
}

export type VideoPreviewListener = (
  state: VideoPreviewSnapshot,
  previous: VideoPreviewSnapshot,
  event: VideoPreviewEvent,
) => void;
