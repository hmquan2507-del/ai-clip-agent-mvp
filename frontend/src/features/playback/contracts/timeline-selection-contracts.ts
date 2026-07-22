export const TIMELINE_SELECTION_CONTRACT_VERSION = "16.8.7.6" as const;

export type TimelineSelectionStatus = "idle" | "ready" | "selecting" | "disposed";
export type TimelineSelectionEventType =
  | "selection_changed"
  | "active_changed"
  | "focus_changed"
  | "history_restored"
  | "reset"
  | "disposed";

export interface TimelineSelectionItem {
  readonly id: string;
  readonly trackId?: string;
  readonly startTimeSeconds?: number;
  readonly endTimeSeconds?: number;
}

export interface TimelineSelectionSnapshot {
  readonly contractVersion: typeof TIMELINE_SELECTION_CONTRACT_VERSION;
  readonly version: number;
  readonly status: TimelineSelectionStatus;
  readonly selectedClipIds: readonly string[];
  readonly activeClipId: string | null;
  readonly focusedClipId: string | null;
  readonly anchorClipId: string | null;
  readonly lastSelectedClipId: string | null;
  readonly selectionCount: number;
  readonly historyDepth: number;
}

export interface TimelineSelectionEvent {
  readonly type: TimelineSelectionEventType;
  readonly snapshot: TimelineSelectionSnapshot;
}

export interface TimelineSelectionConfiguration {
  readonly orderedClipIds?: readonly string[];
  readonly historyLimit?: number;
}

export type TimelineSelectionListener = (event: TimelineSelectionEvent) => void;
