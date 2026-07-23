export const PROFESSIONAL_SELECTION_TOOL_CONTRACT_VERSION = "16.9.3" as const;

export type ProfessionalTimelineTool = "selection" | "razor" | "hand" | "range" | "zoom";
export type ProfessionalSelectionEntityType = "clip" | "track" | "track-group" | "keyframe" | "transition" | "marker" | "range";
export type ProfessionalSelectionMode = "replace" | "add" | "toggle" | "subtract";
export type ProfessionalSelectionEventType =
  | "initialized" | "tool-changed" | "selection-changed" | "marquee-started" | "marquee-updated"
  | "marquee-committed" | "marquee-cancelled" | "range-updated" | "focus-changed"
  | "state-restored" | "reset" | "disposed";

export interface ProfessionalSelectionEntity {
  readonly entityId: string;
  readonly entityType: ProfessionalSelectionEntityType;
  readonly trackId?: string | null;
  readonly groupId?: string | null;
  readonly startTime?: number | null;
  readonly endTime?: number | null;
  readonly metadata?: Readonly<Record<string, unknown>>;
}

export interface TimelineSelectionPoint { readonly x: number; readonly y: number; }
export interface TimelineSelectionRect { readonly left: number; readonly top: number; readonly right: number; readonly bottom: number; }
export interface TimelineSelectableBounds extends ProfessionalSelectionEntity { readonly bounds: TimelineSelectionRect; }
export interface ProfessionalTimelineRangeSelection { readonly startTime: number; readonly endTime: number; readonly trackIds: readonly string[]; }

export interface ProfessionalSelectionConfiguration {
  readonly initialTool?: ProfessionalTimelineTool;
  readonly allowMixedEntityTypes?: boolean;
  readonly preserveSelectionOnToolChange?: boolean;
  readonly marqueeContainment?: "intersect" | "contain";
  readonly maximumSelectionSize?: number | null;
}

export interface ProfessionalSelectionSnapshot {
  readonly contractVersion: typeof PROFESSIONAL_SELECTION_TOOL_CONTRACT_VERSION;
  readonly version: number;
  readonly disposed: boolean;
  readonly activeTool: ProfessionalTimelineTool;
  readonly selectedEntities: readonly ProfessionalSelectionEntity[];
  readonly selectedEntityIds: readonly string[];
  readonly focusedEntityId: string | null;
  readonly marquee: TimelineSelectionRect | null;
  readonly rangeSelection: ProfessionalTimelineRangeSelection | null;
}

export interface ProfessionalSelectionHistoryPort {
  commitSelectionMutation(input: {
    readonly label: string;
    readonly before: ProfessionalSelectionSnapshot;
    readonly after: ProfessionalSelectionSnapshot;
    readonly affectedEntityIds: readonly string[];
  }): void | Promise<void>;
}

export interface ProfessionalSelectionEvent { readonly type: ProfessionalSelectionEventType; readonly snapshot: ProfessionalSelectionSnapshot; }
export type ProfessionalSelectionListener = (event: ProfessionalSelectionEvent) => void;
