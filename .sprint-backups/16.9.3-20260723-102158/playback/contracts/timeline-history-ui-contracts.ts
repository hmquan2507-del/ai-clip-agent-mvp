import type { TimelineHistoryCheckpoint, TimelineHistoryEntry, TimelineHistoryJsonValue } from "./timeline-history-contracts";
import type { TimelineHistoryIntegrationSnapshot } from "./timeline-history-integration-contracts";

export const TIMELINE_HISTORY_UI_CONTRACT_VERSION = 1 as const;

export type TimelineHistoryPanelMode = "closed" | "history" | "checkpoints";
export type TimelineHistoryToastKind = "undo" | "redo" | "checkpoint" | "restore" | "error";

export interface TimelineHistoryToastMessage {
  readonly id: string;
  readonly kind: TimelineHistoryToastKind;
  readonly title: string;
  readonly description: string;
  readonly createdAt: number;
}

export interface TimelineHistoryUiState<TState = TimelineHistoryJsonValue> {
  readonly contractVersion: typeof TIMELINE_HISTORY_UI_CONTRACT_VERSION;
  readonly version: number;
  readonly panelMode: TimelineHistoryPanelMode;
  readonly selectedEntryId: string | null;
  readonly selectedCheckpointId: string | null;
  readonly busy: boolean;
  readonly canUndo: boolean;
  readonly canRedo: boolean;
  readonly undoLabel: string | null;
  readonly redoLabel: string | null;
  readonly entries: readonly TimelineHistoryEntry<TState>[];
  readonly checkpoints: readonly TimelineHistoryCheckpoint<TState>[];
  readonly currentEntryId: string | null;
  readonly toast: TimelineHistoryToastMessage | null;
  readonly integration: TimelineHistoryIntegrationSnapshot<TState>;
}

export interface TimelineHistoryUiActions<TState = TimelineHistoryJsonValue> {
  createCheckpoint?(label: string): void | Promise<void>;
  restoreCheckpoint?(checkpoint: TimelineHistoryCheckpoint<TState>): void | Promise<void>;
  deleteCheckpoint?(checkpoint: TimelineHistoryCheckpoint<TState>): void | Promise<void>;
  previewEntry?(entry: TimelineHistoryEntry<TState>): void | Promise<void>;
}

export type TimelineHistoryUiListener<TState = TimelineHistoryJsonValue> = (state: TimelineHistoryUiState<TState>) => void;
