import type { TimelineHistoryJsonValue } from "./timeline-history-contracts";

export const TIMELINE_EFFECTS_ANIMATION_CONTRACT_VERSION = 1 as const;

export type TimelineInterpolation = "hold" | "linear" | "ease-in" | "ease-out" | "ease-in-out";
export type TimelineAnimatableProperty =
  | "position-x" | "position-y" | "scale-x" | "scale-y" | "rotation" | "opacity"
  | "volume" | "blur" | "brightness" | "contrast" | "saturation";
export type TimelineEffectKind =
  | "transform" | "opacity" | "blur" | "brightness" | "contrast" | "saturation"
  | "color-adjustment" | "audio-gain" | "custom";
export type TimelineTransitionKind =
  | "cut" | "cross-dissolve" | "fade" | "dip-to-black" | "wipe-left" | "wipe-right" | "zoom" | "custom";

export interface TimelineKeyframe {
  readonly keyframeId: string;
  readonly clipId: string;
  readonly property: TimelineAnimatableProperty;
  readonly timeSeconds: number;
  readonly value: number;
  readonly interpolation: TimelineInterpolation;
}

export interface TimelineEvaluatedProperty {
  readonly property: TimelineAnimatableProperty;
  readonly value: number;
  readonly previousKeyframeId: string | null;
  readonly nextKeyframeId: string | null;
  readonly progress: number;
}

export interface TimelineEffectDefinition {
  readonly effectId: string;
  readonly clipId: string;
  readonly kind: TimelineEffectKind;
  readonly label: string;
  readonly enabled: boolean;
  readonly order: number;
  readonly parameters: Readonly<Record<string, TimelineHistoryJsonValue>>;
}

export interface TimelineTransitionDefinition {
  readonly transitionId: string;
  readonly kind: TimelineTransitionKind;
  readonly fromClipId: string;
  readonly toClipId: string;
  readonly startSeconds: number;
  readonly durationSeconds: number;
  readonly enabled: boolean;
  readonly parameters: Readonly<Record<string, TimelineHistoryJsonValue>>;
}

export interface TimelineMotionPreset {
  readonly presetId: string;
  readonly label: string;
  readonly durationSeconds: number;
  readonly keyframes: readonly Omit<TimelineKeyframe, "keyframeId" | "clipId">[];
}

export interface TimelineTransitionEvaluation {
  readonly transitionId: string;
  readonly active: boolean;
  readonly progress: number;
  readonly fromOpacity: number;
  readonly toOpacity: number;
}

export interface TimelineEffectsAnimationSnapshot {
  readonly contractVersion: typeof TIMELINE_EFFECTS_ANIMATION_CONTRACT_VERSION;
  readonly version: number;
  readonly keyframes: readonly TimelineKeyframe[];
  readonly effects: readonly TimelineEffectDefinition[];
  readonly transitions: readonly TimelineTransitionDefinition[];
}

export interface TimelineEffectsAnimationFrame {
  readonly clipId: string;
  readonly timeSeconds: number;
  readonly properties: Readonly<Partial<Record<TimelineAnimatableProperty, number>>>;
  readonly evaluated: readonly TimelineEvaluatedProperty[];
  readonly effects: readonly TimelineEffectDefinition[];
  readonly transitions: readonly TimelineTransitionEvaluation[];
}
