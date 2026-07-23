import type {
  TimelineHistoryChange,
  TimelineHistoryConflict,
  TimelineHistoryJsonValue,
  TimelineHistoryOperationKind,
  TimelineHistoryRecordResult,
  TimelineHistoryRestoreResult,
  TimelineHistoryStatePayload,
  TimelineUndoRedoHistoryConfiguration,
  TimelineUndoRedoHistorySnapshot,
} from "./timeline-history-contracts";

export const TIMELINE_HISTORY_INTEGRATION_CONTRACT_VERSION = 1 as const;

export type TimelineHistoryIntegrationStatus =
  | "idle"
  | "executing-command"
  | "restoring"
  | "persisting"
  | "blocked"
  | "disposed";

export interface TimelineHistoryStateAdapter<TState = TimelineHistoryJsonValue> {
  captureState(): TimelineHistoryStatePayload<TState> | Promise<TimelineHistoryStatePayload<TState>>;
  restoreState(
    payload: TimelineHistoryStatePayload<TState>,
    context: TimelineHistoryRestoreContext,
  ): void | Promise<void>;
}

export interface TimelineHistoryRestoreContext {
  readonly direction: "undo" | "redo" | "workspace-restore";
  readonly entryId: string | null;
  readonly source: "runtime" | "keyboard" | "toolbar" | "workspace" | "api";
}

export interface TimelineHistoryCommandExecutionContext<TState = TimelineHistoryJsonValue> {
  readonly before: TimelineHistoryStatePayload<TState>;
}

export interface TimelineHistoryCommandExecutionResult<TState = TimelineHistoryJsonValue> {
  readonly after?: TimelineHistoryStatePayload<TState>;
  readonly changes: readonly TimelineHistoryChange[];
  readonly metadata?: Readonly<Record<string, TimelineHistoryJsonValue>>;
}

export interface TimelineHistoryCommand<TState = TimelineHistoryJsonValue> {
  readonly commandId: string;
  readonly operation: TimelineHistoryOperationKind;
  readonly label: string;
  readonly sourceRuntime: string;
  readonly mergeKey?: string | null;
  readonly metadata?: Readonly<Record<string, TimelineHistoryJsonValue>>;
  execute(
    context: TimelineHistoryCommandExecutionContext<TState>,
  ): TimelineHistoryCommandExecutionResult<TState> | Promise<TimelineHistoryCommandExecutionResult<TState>>;
}

export interface TimelineHistoryCommandResult<TState = TimelineHistoryJsonValue> {
  readonly executed: boolean;
  readonly commandId: string;
  readonly before: TimelineHistoryStatePayload<TState> | null;
  readonly after: TimelineHistoryStatePayload<TState> | null;
  readonly recordResult: TimelineHistoryRecordResult<TState> | null;
  readonly conflicts: readonly TimelineHistoryConflict[];
  readonly error: Error | null;
}

export interface TimelineHistoryIntegrationConfiguration {
  readonly history?: TimelineUndoRedoHistoryConfiguration;
  readonly restoreOnCommandFailure?: boolean;
  readonly rejectUnchangedState?: boolean;
  readonly persistAfterMutation?: boolean;
  readonly persistenceKey?: string;
}

export interface TimelineHistoryIntegrationSnapshot<TState = TimelineHistoryJsonValue> {
  readonly contractVersion: typeof TIMELINE_HISTORY_INTEGRATION_CONTRACT_VERSION;
  readonly version: number;
  readonly status: TimelineHistoryIntegrationStatus;
  readonly initialized: boolean;
  readonly busy: boolean;
  readonly canUndo: boolean;
  readonly canRedo: boolean;
  readonly undoLabel: string | null;
  readonly redoLabel: string | null;
  readonly lastCommandId: string | null;
  readonly lastError: string | null;
  readonly history: TimelineUndoRedoHistorySnapshot<TState>;
}

export interface TimelineHistoryIntegrationEvent<TState = TimelineHistoryJsonValue> {
  readonly type:
    | "initialized"
    | "command-executed"
    | "undo-completed"
    | "redo-completed"
    | "workspace-restored"
    | "persistence-completed"
    | "blocked"
    | "disposed";
  readonly snapshot: TimelineHistoryIntegrationSnapshot<TState>;
}

export type TimelineHistoryIntegrationListener<TState = TimelineHistoryJsonValue> =
  (event: TimelineHistoryIntegrationEvent<TState>) => void;

export interface TimelineHistoryUndoRedoResult<TState = TimelineHistoryJsonValue> {
  readonly completed: boolean;
  readonly restoreResult: TimelineHistoryRestoreResult<TState>;
  readonly error: Error | null;
}

export interface TimelineHistoryKeyboardEventLike {
  readonly key: string;
  readonly ctrlKey?: boolean;
  readonly metaKey?: boolean;
  readonly shiftKey?: boolean;
  readonly altKey?: boolean;
  readonly target?: EventTarget | null;
  preventDefault(): void;
}

export interface TimelineHistoryKeyboardConfiguration {
  readonly allowInEditableTargets?: boolean;
  readonly useMetaKey?: boolean;
  readonly useControlKey?: boolean;
}

export interface TimelineHistoryToolbarState {
  readonly canUndo: boolean;
  readonly canRedo: boolean;
  readonly undoLabel: string | null;
  readonly redoLabel: string | null;
  readonly busy: boolean;
}
