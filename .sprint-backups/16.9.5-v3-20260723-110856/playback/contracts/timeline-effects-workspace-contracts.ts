import type {
  TimelineAnimatableProperty,
  TimelineEffectDefinition,
  TimelineEffectsAnimationFrame,
  TimelineInterpolation,
  TimelineKeyframe,
  TimelineMotionPreset,
  TimelineTransitionDefinition,
} from "./timeline-effects-animation-contracts";

export const TIMELINE_EFFECTS_WORKSPACE_CONTRACT_VERSION = 1 as const;

export type TimelineEffectsWorkspaceStatus = "detached" | "idle" | "applying" | "error" | "disposed";

export interface TimelineEffectsWorkspaceSelectionPort {
  getSelectedClipIds(): readonly string[];
  subscribe(listener: (clipIds: readonly string[]) => void): () => void;
}

export interface TimelineEffectsWorkspacePlayheadPort {
  getCurrentTimeSeconds(): number;
  subscribe(listener: (timeSeconds: number) => void): () => void;
}

export interface TimelineEffectsPreviewPort {
  applyFrame(frame: TimelineEffectsAnimationFrame): void | Promise<void>;
  clear(clipId?: string): void | Promise<void>;
}

export interface TimelineEffectsWorkspaceState {
  readonly contractVersion: typeof TIMELINE_EFFECTS_WORKSPACE_CONTRACT_VERSION;
  readonly version: number;
  readonly status: TimelineEffectsWorkspaceStatus;
  readonly attached: boolean;
  readonly busy: boolean;
  readonly selectedClipIds: readonly string[];
  readonly activeClipId: string | null;
  readonly currentTimeSeconds: number;
  readonly frame: TimelineEffectsAnimationFrame | null;
  readonly keyframes: readonly TimelineKeyframe[];
  readonly effects: readonly TimelineEffectDefinition[];
  readonly transitions: readonly TimelineTransitionDefinition[];
  readonly presets: readonly TimelineMotionPreset[];
  readonly lastError: string | null;
}

export interface TimelineEffectsWorkspaceDependencies {
  readonly selection?: TimelineEffectsWorkspaceSelectionPort;
  readonly playhead?: TimelineEffectsWorkspacePlayheadPort;
  readonly preview?: TimelineEffectsPreviewPort;
}

export interface TimelineEffectsAddKeyframeInput {
  readonly property: TimelineAnimatableProperty;
  readonly value: number;
  readonly timeSeconds?: number;
  readonly interpolation?: TimelineInterpolation;
}

export interface TimelineEffectsAddEffectInput {
  readonly kind: TimelineEffectDefinition["kind"];
  readonly label: string;
  readonly parameters?: TimelineEffectDefinition["parameters"];
}

export type TimelineEffectsWorkspaceListener = (state: TimelineEffectsWorkspaceState) => void;
