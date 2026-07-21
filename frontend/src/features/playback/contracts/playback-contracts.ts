export const PLAYBACK_SESSION_CONTRACT_VERSION = "16.8.7.1" as const;

export type PlaybackSessionStatus =
  | "idle"
  | "ready"
  | "playing"
  | "paused"
  | "seeking"
  | "stopped"
  | "completed"
  | "disposed";

export type PlaybackDirection = 1 | -1;

export type PlaybackSessionEventType =
  | "ready"
  | "started"
  | "paused"
  | "stopped"
  | "seeked"
  | "speed-changed"
  | "loop-changed"
  | "stepped"
  | "advanced"
  | "completed"
  | "looped"
  | "reset";

export interface PlaybackSessionConfiguration {
  duration: number;
  fps: number;
  initialTime?: number;
  initialSpeed?: number;
  initialLoop?: boolean;
  initialDirection?: PlaybackDirection;
}

export interface PlaybackSessionState {
  contractVersion: typeof PLAYBACK_SESSION_CONTRACT_VERSION;
  status: PlaybackSessionStatus;
  duration: number;
  fps: number;
  currentTime: number;
  currentFrame: number;
  speed: number;
  loop: boolean;
  direction: PlaybackDirection;
  playing: boolean;
  stateRevision: number;
  updatedAt: string | null;
}

export interface PlaybackSessionEvent {
  type: PlaybackSessionEventType;
  stateRevision: number;
  occurredAt: string;
}

export type PlaybackSessionListener = (
  state: PlaybackSessionState,
  previous: PlaybackSessionState,
  event: PlaybackSessionEvent,
) => void;
