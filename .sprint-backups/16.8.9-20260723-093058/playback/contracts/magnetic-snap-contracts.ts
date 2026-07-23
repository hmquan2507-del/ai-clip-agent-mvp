export const TIMELINE_MAGNETIC_SNAP_CONTRACT_VERSION = "16.8.8.1" as const;

export type TimelineSnapTargetType =
  | "timeline-start" | "timeline-end" | "playhead" | "marker"
  | "clip-start" | "clip-end" | "subtitle-start" | "subtitle-end" | "custom";
export type TimelineSnapSourceEdge = "start" | "end" | "position";
export type TimelineMagneticSnapStatus = "idle" | "ready" | "previewing" | "disposed";
export type TimelineMagneticSnapEventType =
  | "configured" | "targets_replaced" | "targets_added" | "targets_removed"
  | "targets_cleared" | "snap_resolved" | "magnetic_preview_updated"
  | "preview_cleared" | "reset" | "disposed";

export interface TimelineSnapTarget {
  readonly targetId: string;
  readonly type: TimelineSnapTargetType;
  readonly frame: number;
  readonly trackId?: string | null;
  readonly ownerId?: string | null;
  readonly label?: string | null;
  readonly priority?: number;
  readonly enabled?: boolean;
}
export interface TimelineSnapSource {
  readonly sourceId: string;
  readonly ownerId?: string | null;
  readonly trackId?: string | null;
  readonly edge: TimelineSnapSourceEdge;
  readonly frame: number;
}
export interface TimelineMagneticSnapConfiguration {
  readonly framesPerSecond: number;
  readonly enabled?: boolean;
  readonly magneticEnabled?: boolean;
  readonly thresholdFrames?: number;
  readonly thresholdPixels?: number;
  readonly pixelsPerSecond?: number;
  readonly zoom?: number;
  readonly timelineStartFrame?: number;
  readonly timelineEndFrame?: number;
  readonly preferSameTrack?: boolean;
  readonly sameTrackPriorityBoost?: number;
  readonly targetTypePriorities?: Partial<Readonly<Record<TimelineSnapTargetType, number>>>;
}
export interface TimelineSnapCandidate {
  readonly sourceId: string;
  readonly sourceEdge: TimelineSnapSourceEdge;
  readonly sourceFrame: number;
  readonly targetId: string;
  readonly targetType: TimelineSnapTargetType;
  readonly targetFrame: number;
  readonly deltaFrames: number;
  readonly absoluteDistanceFrames: number;
  readonly distancePixels: number | null;
  readonly basePriority: number;
  readonly effectivePriority: number;
  readonly sameTrack: boolean;
}
export interface TimelineSnapGuide {
  readonly guideId: string;
  readonly frame: number;
  readonly targetId: string;
  readonly targetType: TimelineSnapTargetType;
  readonly label: string | null;
  readonly sourceIds: readonly string[];
}
export interface TimelineSnapResult {
  readonly snapped: boolean;
  readonly originalFrame: number;
  readonly resolvedFrame: number;
  readonly deltaFrames: number;
  readonly sourceId: string;
  readonly sourceEdge: TimelineSnapSourceEdge;
  readonly targetId: string | null;
  readonly targetType: TimelineSnapTargetType | null;
  readonly targetFrame: number | null;
  readonly candidateCount: number;
  readonly guide: TimelineSnapGuide | null;
}
export interface ResolveTimelineSnapRequest {
  readonly source: TimelineSnapSource;
  readonly targets?: readonly TimelineSnapTarget[];
  readonly excludeTargetIds?: readonly string[];
  readonly excludeOwnerIds?: readonly string[];
  readonly allowedTargetTypes?: readonly TimelineSnapTargetType[];
  readonly trackId?: string | null;
}
export interface PreviewMagneticMoveRequest {
  readonly sources: readonly TimelineSnapSource[];
  readonly proposedDeltaFrames: number;
  readonly excludeTargetIds?: readonly string[];
  readonly excludeOwnerIds?: readonly string[];
  readonly allowedTargetTypes?: readonly TimelineSnapTargetType[];
}
export interface PreviewMagneticTrimRequest {
  readonly source: TimelineSnapSource;
  readonly proposedFrame: number;
  readonly excludeTargetIds?: readonly string[];
  readonly excludeOwnerIds?: readonly string[];
  readonly allowedTargetTypes?: readonly TimelineSnapTargetType[];
}
export interface TimelineMagneticPreview {
  readonly originalFrames: readonly number[];
  readonly resolvedFrames: readonly number[];
  readonly primaryResult: TimelineSnapResult;
  readonly guides: readonly TimelineSnapGuide[];
}
export interface TimelineMagneticSnapSnapshot {
  readonly contractVersion: typeof TIMELINE_MAGNETIC_SNAP_CONTRACT_VERSION;
  readonly version: number;
  readonly status: TimelineMagneticSnapStatus;
  readonly configured: boolean;
  readonly enabled: boolean;
  readonly magneticEnabled: boolean;
  readonly targetCount: number;
  readonly targets: readonly TimelineSnapTarget[];
  readonly lastResult: TimelineSnapResult | null;
  readonly activeGuides: readonly TimelineSnapGuide[];
}
export interface TimelineMagneticSnapEvent { readonly type: TimelineMagneticSnapEventType; readonly snapshot: TimelineMagneticSnapSnapshot; }
export type TimelineMagneticSnapListener = (event: TimelineMagneticSnapEvent) => void;
