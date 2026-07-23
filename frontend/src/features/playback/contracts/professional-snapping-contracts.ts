export const PROFESSIONAL_SNAPPING_CONTRACT_VERSION = "16.9.4" as const;

export type ProfessionalSnapSource =
  | "clip-start" | "clip-end" | "playhead" | "marker" | "keyframe"
  | "transition-start" | "transition-end" | "audio-peak" | "subtitle-cue"
  | "timeline-start" | "timeline-end" | "custom";

export type ProfessionalSnapAxis = "time" | "vertical";
export type ProfessionalSnapStrength = "soft" | "normal" | "strong";

export interface ProfessionalSnapCandidate {
  readonly candidateId: string;
  readonly source: ProfessionalSnapSource;
  readonly time: number;
  readonly trackId?: string | null;
  readonly entityId?: string | null;
  readonly priority?: number;
  readonly metadata?: Readonly<Record<string, unknown>>;
}

export interface ProfessionalSnapRequest {
  readonly proposedTime: number;
  readonly movingEntityIds?: readonly string[];
  readonly activeTrackId?: string | null;
  readonly pixelsPerSecond?: number;
  readonly thresholdPixels?: number;
  readonly thresholdSeconds?: number;
  readonly disabledSources?: readonly ProfessionalSnapSource[];
  readonly includeOtherTracks?: boolean;
  readonly forceDisable?: boolean;
}

export interface ProfessionalSnapMatch {
  readonly candidate: ProfessionalSnapCandidate;
  readonly proposedTime: number;
  readonly snappedTime: number;
  readonly deltaSeconds: number;
  readonly distancePixels: number | null;
  readonly score: number;
  readonly strength: ProfessionalSnapStrength;
}

export interface ProfessionalSnapGuide {
  readonly guideId: string;
  readonly time: number;
  readonly source: ProfessionalSnapSource;
  readonly label: string;
  readonly deltaSeconds: number;
  readonly distancePixels: number | null;
  readonly trackId: string | null;
  readonly entityId: string | null;
  readonly visible: boolean;
}

export interface ProfessionalMagneticPreview {
  readonly active: boolean;
  readonly originalTime: number;
  readonly previewTime: number;
  readonly displacementSeconds: number;
  readonly match: ProfessionalSnapMatch | null;
  readonly guides: readonly ProfessionalSnapGuide[];
}

export interface ProfessionalSnappingConfiguration {
  readonly enabled?: boolean;
  readonly frameRate?: number;
  readonly defaultThresholdPixels?: number;
  readonly defaultThresholdSeconds?: number;
  readonly frameAccurate?: boolean;
  readonly preferSameTrack?: boolean;
  readonly sourcePriorities?: Partial<Record<ProfessionalSnapSource, number>>;
}

export interface ProfessionalSnappingSnapshot {
  readonly contractVersion: typeof PROFESSIONAL_SNAPPING_CONTRACT_VERSION;
  readonly version: number;
  readonly disposed: boolean;
  readonly enabled: boolean;
  readonly candidateCount: number;
  readonly candidates: readonly ProfessionalSnapCandidate[];
  readonly activePreview: ProfessionalMagneticPreview | null;
}

export type ProfessionalSnappingEventType =
  | "initialized" | "enabled-changed" | "candidates-changed"
  | "preview-updated" | "preview-cleared" | "snap-committed"
  | "state-restored" | "reset" | "disposed";

export interface ProfessionalSnappingEvent {
  readonly type: ProfessionalSnappingEventType;
  readonly snapshot: ProfessionalSnappingSnapshot;
}

export type ProfessionalSnappingListener = (event: ProfessionalSnappingEvent) => void;

export interface ProfessionalSnappingHistoryPort {
  commitSnappingMutation(input: {
    readonly label: string;
    readonly before: ProfessionalSnappingSnapshot;
    readonly after: ProfessionalSnappingSnapshot;
    readonly affectedEntityIds: readonly string[];
  }): void | Promise<void>;
}
