export const AUDIO_SYNCHRONIZATION_CONTRACT_VERSION = "16.8.7.4" as const;

export type AudioTrackKind = "voice" | "music" | "sfx";
export type AudioSynchronizationStatus =
  | "idle"
  | "ready"
  | "playing"
  | "paused"
  | "seeking"
  | "buffering"
  | "stopped"
  | "error"
  | "disposed";

export type AudioPreviewEventName =
  | "loadedmetadata"
  | "timeupdate"
  | "seeking"
  | "seeked"
  | "ended"
  | "waiting"
  | "playing"
  | "pause"
  | "error";

export interface AudioPreviewPort {
  readonly currentTime: number;
  readonly duration: number;
  readonly paused: boolean;
  readonly seeking: boolean;
  readonly ended: boolean;
  readonly playbackRate: number;
  readonly volume: number;
  readonly muted: boolean;
  play(): Promise<void>;
  pause(): void;
  setCurrentTime(value: number): void;
  setPlaybackRate(value: number): void;
  setVolume(value: number): void;
  setMuted(value: boolean): void;
  subscribe(event: AudioPreviewEventName, listener: () => void): () => void;
}

export interface AudioTrackDescriptor {
  readonly id: string;
  readonly kind: AudioTrackKind;
  readonly startTimeSeconds: number;
  readonly endTimeSeconds: number;
  readonly sourceOffsetSeconds: number;
  readonly volume: number;
  readonly muted: boolean;
  readonly solo: boolean;
  readonly enabled: boolean;
}

export interface AudioTrackSnapshot extends AudioTrackDescriptor {
  readonly attached: boolean;
  readonly active: boolean;
  readonly buffering: boolean;
  readonly driftSeconds: number;
  readonly effectiveVolume: number;
  readonly sourceTimeSeconds: number;
  readonly errorMessage: string | null;
}

export interface AudioSynchronizationConfiguration {
  fps: number;
  masterVolume?: number;
  masterMuted?: boolean;
  driftThreshold?: number;
  largeDriftThreshold?: number;
}

export interface AudioSynchronizationSnapshot {
  contractVersion: typeof AUDIO_SYNCHRONIZATION_CONTRACT_VERSION;
  status: AudioSynchronizationStatus;
  currentTimeSeconds: number;
  playbackRate: number;
  masterVolume: number;
  masterMuted: boolean;
  activeTrackIds: readonly string[];
  bufferingTrackIds: readonly string[];
  driftedTrackIds: readonly string[];
  tracks: readonly AudioTrackSnapshot[];
  stateRevision: number;
  updatedAt: string | null;
}

export type AudioSynchronizationEventType =
  | "track-attached"
  | "track-detached"
  | "tracks-detached"
  | "play-synced"
  | "pause-synced"
  | "stop-synced"
  | "seek-synced"
  | "rate-synced"
  | "volume-changed"
  | "mute-changed"
  | "solo-changed"
  | "buffering-started"
  | "buffering-ended"
  | "error"
  | "reset";

export interface AudioSynchronizationEvent {
  type: AudioSynchronizationEventType;
  trackId?: string;
  stateRevision: number;
  occurredAt: string;
}

export type AudioSynchronizationListener = (
  state: AudioSynchronizationSnapshot,
  previous: AudioSynchronizationSnapshot,
  event: AudioSynchronizationEvent,
) => void;
