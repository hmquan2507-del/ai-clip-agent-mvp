export const PROFESSIONAL_MULTI_TRACK_CONTRACT_VERSION = "16.9.2" as const;

export type ProfessionalTrackKind = "video" | "audio" | "subtitle" | "overlay" | "effect" | "adjustment" | "custom";
export type ProfessionalTrackStatus = "active" | "archived";
export type ProfessionalMultiTrackEventType =
  | "initialized" | "track-added" | "track-removed" | "track-updated" | "track-reordered"
  | "track-duplicated" | "track-group-created" | "track-group-updated" | "track-group-removed"
  | "clip-assigned" | "clip-unassigned" | "state-restored" | "reset" | "disposed";

export interface ProfessionalTrack {
  readonly trackId: string;
  readonly name: string;
  readonly kind: ProfessionalTrackKind;
  readonly order: number;
  readonly color: string | null;
  readonly locked: boolean;
  readonly muted: boolean;
  readonly solo: boolean;
  readonly hidden: boolean;
  readonly collapsed: boolean;
  readonly rippleEnabled: boolean;
  readonly magneticEnabled: boolean;
  readonly groupId: string | null;
  readonly status: ProfessionalTrackStatus;
  readonly metadata: Readonly<Record<string, unknown>>;
}

export interface ProfessionalTrackGroup {
  readonly groupId: string;
  readonly name: string;
  readonly color: string | null;
  readonly collapsed: boolean;
  readonly locked: boolean;
  readonly trackIds: readonly string[];
}

export interface ProfessionalTrackClipAssignment {
  readonly clipId: string;
  readonly trackId: string;
}

export interface ProfessionalMultiTrackConfiguration {
  readonly maxTracks?: number | null;
  readonly allowEmptyTimeline?: boolean;
  readonly enforceUniqueNames?: boolean;
  readonly defaultTrackColor?: string | null;
  readonly autoRenameDuplicates?: boolean;
  readonly soloIsExclusive?: boolean;
}

export interface AddProfessionalTrackRequest {
  readonly trackId: string;
  readonly name?: string;
  readonly kind: ProfessionalTrackKind;
  readonly order?: number;
  readonly color?: string | null;
  readonly groupId?: string | null;
  readonly metadata?: Readonly<Record<string, unknown>>;
}

export interface UpdateProfessionalTrackRequest {
  readonly name?: string;
  readonly color?: string | null;
  readonly locked?: boolean;
  readonly muted?: boolean;
  readonly solo?: boolean;
  readonly hidden?: boolean;
  readonly collapsed?: boolean;
  readonly rippleEnabled?: boolean;
  readonly magneticEnabled?: boolean;
  readonly groupId?: string | null;
  readonly status?: ProfessionalTrackStatus;
  readonly metadata?: Readonly<Record<string, unknown>>;
}

export interface ProfessionalMultiTrackSnapshot {
  readonly contractVersion: typeof PROFESSIONAL_MULTI_TRACK_CONTRACT_VERSION;
  readonly version: number;
  readonly disposed: boolean;
  readonly tracks: readonly ProfessionalTrack[];
  readonly groups: readonly ProfessionalTrackGroup[];
  readonly assignments: readonly ProfessionalTrackClipAssignment[];
  readonly audibleTrackIds: readonly string[];
  readonly visibleTrackIds: readonly string[];
  readonly lockedTrackIds: readonly string[];
}

export interface ProfessionalMultiTrackHistoryPort {
  commitTrackMutation(input: {
    readonly label: string;
    readonly before: ProfessionalMultiTrackSnapshot;
    readonly after: ProfessionalMultiTrackSnapshot;
    readonly affectedTrackIds: readonly string[];
  }): void | Promise<void>;
}

export interface ProfessionalMultiTrackEvent {
  readonly type: ProfessionalMultiTrackEventType;
  readonly snapshot: ProfessionalMultiTrackSnapshot;
}

export type ProfessionalMultiTrackListener = (event: ProfessionalMultiTrackEvent) => void;
