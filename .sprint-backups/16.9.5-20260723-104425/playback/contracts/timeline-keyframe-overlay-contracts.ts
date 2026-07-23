import type { TimelineAnimatableProperty, TimelineInterpolation, TimelineKeyframe } from "./timeline-effects-animation-contracts";

export const TIMELINE_KEYFRAME_OVERLAY_CONTRACT_VERSION = 1 as const;

export type TimelineKeyframeSnapKind = "none" | "playhead" | "marker" | "clip-start" | "clip-end" | "keyframe";
export type TimelineKeyframeLaneDensity = "compact" | "comfortable";

export interface TimelineKeyframeLaneGeometry {
  readonly clipId: string;
  readonly clipStartSeconds: number;
  readonly clipEndSeconds: number;
  readonly pixelsPerSecond: number;
  readonly viewportStartSeconds: number;
  readonly viewportEndSeconds: number;
}

export interface TimelineKeyframeOverlayPoint {
  readonly keyframeId: string;
  readonly clipId: string;
  readonly property: TimelineAnimatableProperty;
  readonly interpolation: TimelineInterpolation;
  readonly timeSeconds: number;
  readonly value: number;
  readonly x: number;
  readonly selected: boolean;
  readonly hovered: boolean;
}

export interface TimelineAnimationRangeOverlay {
  readonly clipId: string;
  readonly property: TimelineAnimatableProperty;
  readonly startSeconds: number;
  readonly endSeconds: number;
  readonly startX: number;
  readonly endX: number;
  readonly keyframeCount: number;
}

export interface TimelineKeyframeSnapCandidate {
  readonly kind: Exclude<TimelineKeyframeSnapKind, "none">;
  readonly timeSeconds: number;
  readonly priority: number;
  readonly sourceId: string;
}

export interface TimelineKeyframeSnapResult {
  readonly snapped: boolean;
  readonly kind: TimelineKeyframeSnapKind;
  readonly requestedTimeSeconds: number;
  readonly resolvedTimeSeconds: number;
  readonly distanceSeconds: number;
  readonly sourceId: string | null;
}

export interface TimelineKeyframeDragPreview {
  readonly keyframeIds: readonly string[];
  readonly deltaSeconds: number;
  readonly targetTimes: Readonly<Record<string, number>>;
  readonly snap: TimelineKeyframeSnapResult;
}

export interface TimelineKeyframeOverlayState {
  readonly contractVersion: typeof TIMELINE_KEYFRAME_OVERLAY_CONTRACT_VERSION;
  readonly version: number;
  readonly clipId: string | null;
  readonly expanded: boolean;
  readonly density: TimelineKeyframeLaneDensity;
  readonly selectedKeyframeIds: readonly string[];
  readonly hoveredKeyframeId: string | null;
  readonly points: readonly TimelineKeyframeOverlayPoint[];
  readonly ranges: readonly TimelineAnimationRangeOverlay[];
  readonly dragPreview: TimelineKeyframeDragPreview | null;
}

export interface TimelineKeyframeMutationPort {
  moveKeyframe(keyframeId: string, timeSeconds: number, value?: number): TimelineKeyframe;
  removeKeyframe(keyframeId: string): boolean;
  addKeyframe(keyframe: TimelineKeyframe): TimelineKeyframe;
  getKeyframes(clipId?: string, property?: TimelineAnimatableProperty): readonly TimelineKeyframe[];
}
