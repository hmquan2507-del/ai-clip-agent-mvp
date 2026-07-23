export const TIMELINE_UNDO_REDO_HISTORY_CONTRACT_VERSION = "16.8.8.6" as const;

export type TimelineHistoryJsonPrimitive = string | number | boolean | null;
export type TimelineHistoryJsonValue =
  | TimelineHistoryJsonPrimitive
  | readonly TimelineHistoryJsonValue[]
  | { readonly [key: string]: TimelineHistoryJsonValue };

export type TimelineHistoryOperationKind =
  | "clip-move"
  | "clip-trim-start"
  | "clip-trim-end"
  | "ripple-move"
  | "ripple-insert"
  | "ripple-delete"
  | "slip"
  | "slide"
  | "roll"
  | "multi-track-move"
  | "multi-track-trim"
  | "link-group-create"
  | "link-group-update"
  | "link-group-remove"
  | "sync-repair"
  | "selection-change"
  | "custom";

export type TimelineUndoRedoHistoryStatus =
  | "idle"
  | "recording"
  | "transaction-open"
  | "restoring"
  | "blocked"
  | "disposed";

export type TimelineHistoryConflictCode =
  | "not-configured"
  | "disposed"
  | "missing-entry-id"
  | "missing-transaction-id"
  | "missing-checkpoint-id"
  | "duplicate-entry-id"
  | "duplicate-transaction-id"
  | "duplicate-checkpoint-id"
  | "transaction-already-open"
  | "transaction-not-open"
  | "transaction-id-mismatch"
  | "empty-transaction"
  | "empty-change-set"
  | "invalid-state-version"
  | "invalid-timeline-version"
  | "state-version-conflict"
  | "timeline-version-conflict"
  | "checksum-mismatch"
  | "expected-entry-mismatch"
  | "undo-unavailable"
  | "redo-unavailable"
  | "checkpoint-not-found"
  | "checkpoint-protected"
  | "restore-failed"
  | "history-capacity-exceeded"
  | "invalid-merge-window"
  | "merge-incompatible"
  | "invalid-configuration"
  | "invalid-state-payload";

export interface TimelineHistoryConflict {
  readonly code: TimelineHistoryConflictCode;
  readonly message: string;
  readonly blocking: boolean;
  readonly entryId?: string | null;
  readonly transactionId?: string | null;
  readonly checkpointId?: string | null;
  readonly expectedVersion?: number | null;
  readonly actualVersion?: number | null;
}

export interface TimelineHistoryStatePayload<TState = TimelineHistoryJsonValue> {
  readonly state: TState;
  readonly stateVersion: number;
  readonly timelineVersion: number;
  readonly checksum: string;
  readonly capturedAt: number;
}

export type TimelineHistoryChangeKind = "create" | "update" | "delete" | "reorder" | "replace" | "custom";

export interface TimelineHistoryChange<TValue = TimelineHistoryJsonValue> {
  readonly changeId: string;
  readonly kind: TimelineHistoryChangeKind;
  readonly entityType: string;
  readonly entityId: string;
  readonly path?: string | null;
  readonly before: TValue | null;
  readonly after: TValue | null;
  readonly metadata?: Readonly<Record<string, TimelineHistoryJsonValue>>;
}

export interface TimelineHistoryEntry<TState = TimelineHistoryJsonValue> {
  readonly entryId: string;
  readonly operation: TimelineHistoryOperationKind;
  readonly label: string;
  readonly sourceRuntime: string;
  readonly mergeKey: string | null;
  readonly transactionId: string | null;
  readonly branchId: string;
  readonly sequence: number;
  readonly before: TimelineHistoryStatePayload<TState>;
  readonly after: TimelineHistoryStatePayload<TState>;
  readonly changes: readonly TimelineHistoryChange[];
  readonly createdAt: number;
  readonly metadata: Readonly<Record<string, TimelineHistoryJsonValue>>;
}

export interface TimelineHistoryTransaction<TState = TimelineHistoryJsonValue> {
  readonly transactionId: string;
  readonly label: string;
  readonly operation: TimelineHistoryOperationKind;
  readonly sourceRuntime: string;
  readonly mergeKey: string | null;
  readonly branchId: string;
  readonly startedAt: number;
  readonly baseline: TimelineHistoryStatePayload<TState>;
  readonly changes: readonly TimelineHistoryChange[];
  readonly metadata: Readonly<Record<string, TimelineHistoryJsonValue>>;
}

export interface TimelineHistoryBranch {
  readonly branchId: string;
  readonly parentBranchId: string | null;
  readonly forkedFromEntryId: string | null;
  readonly createdAt: number;
  readonly entryIds: readonly string[];
  readonly active: boolean;
}

export interface TimelineHistoryCheckpoint<TState = TimelineHistoryJsonValue> {
  readonly checkpointId: string;
  readonly label: string;
  readonly entryId: string | null;
  readonly branchId: string;
  readonly state: TimelineHistoryStatePayload<TState>;
  readonly protected: boolean;
  readonly createdAt: number;
  readonly metadata: Readonly<Record<string, TimelineHistoryJsonValue>>;
}

export interface TimelineHistoryMergeDecision<TState = TimelineHistoryJsonValue> {
  readonly mergeable: boolean;
  readonly reason: string;
  readonly mergedEntry: TimelineHistoryEntry<TState> | null;
}

export interface TimelineHistoryPeekResult<TState = TimelineHistoryJsonValue> {
  readonly available: boolean;
  readonly entry: TimelineHistoryEntry<TState> | null;
  readonly conflicts: readonly TimelineHistoryConflict[];
}

export interface TimelineHistoryRecordResult<TState = TimelineHistoryJsonValue> {
  readonly recorded: boolean;
  readonly merged: boolean;
  readonly entry: TimelineHistoryEntry<TState> | null;
  readonly evictedEntryIds: readonly string[];
  readonly clearedFutureEntryIds: readonly string[];
  readonly branch: TimelineHistoryBranch | null;
  readonly conflicts: readonly TimelineHistoryConflict[];
}

export interface TimelineHistoryRestoreResult<TState = TimelineHistoryJsonValue> {
  readonly restored: boolean;
  readonly direction: "undo" | "redo" | "checkpoint";
  readonly entry: TimelineHistoryEntry<TState> | null;
  readonly checkpoint: TimelineHistoryCheckpoint<TState> | null;
  readonly state: TimelineHistoryStatePayload<TState> | null;
  readonly conflicts: readonly TimelineHistoryConflict[];
}

export interface TimelineHistoryTransactionResult<TState = TimelineHistoryJsonValue> {
  readonly committed: boolean;
  readonly transaction: TimelineHistoryTransaction<TState> | null;
  readonly recordResult: TimelineHistoryRecordResult<TState> | null;
  readonly conflicts: readonly TimelineHistoryConflict[];
}

export interface TimelineHistoryCheckpointResult<TState = TimelineHistoryJsonValue> {
  readonly created: boolean;
  readonly checkpoint: TimelineHistoryCheckpoint<TState> | null;
  readonly evictedCheckpointIds: readonly string[];
  readonly conflicts: readonly TimelineHistoryConflict[];
}

export interface TimelineUndoRedoHistoryConfiguration {
  readonly maxEntries?: number;
  readonly maxCheckpoints?: number;
  readonly mergeWindowMs?: number;
  readonly preserveBranches?: boolean;
  readonly recordSelectionChanges?: boolean;
  readonly protectCheckpointEntries?: boolean;
  readonly validateChecksums?: boolean;
  readonly requireContiguousStateVersions?: boolean;
  readonly requireContiguousTimelineVersions?: boolean;
}

export interface ReplaceTimelineHistoryBaselineRequest<TState = TimelineHistoryJsonValue> {
  readonly state: TimelineHistoryStatePayload<TState>;
  readonly clearHistory?: boolean;
  readonly clearCheckpoints?: boolean;
  readonly branchId?: string;
}

export interface RecordTimelineHistoryEntryRequest<TState = TimelineHistoryJsonValue> {
  readonly entryId: string;
  readonly operation: TimelineHistoryOperationKind;
  readonly label: string;
  readonly sourceRuntime: string;
  readonly before: TimelineHistoryStatePayload<TState>;
  readonly after: TimelineHistoryStatePayload<TState>;
  readonly changes: readonly TimelineHistoryChange[];
  readonly mergeKey?: string | null;
  readonly createdAt?: number;
  readonly metadata?: Readonly<Record<string, TimelineHistoryJsonValue>>;
}

export interface BeginTimelineHistoryTransactionRequest<TState = TimelineHistoryJsonValue> {
  readonly transactionId: string;
  readonly operation: TimelineHistoryOperationKind;
  readonly label: string;
  readonly sourceRuntime: string;
  readonly baseline: TimelineHistoryStatePayload<TState>;
  readonly mergeKey?: string | null;
  readonly startedAt?: number;
  readonly metadata?: Readonly<Record<string, TimelineHistoryJsonValue>>;
}

export interface AppendTimelineHistoryTransactionChangeRequest {
  readonly transactionId: string;
  readonly change: TimelineHistoryChange;
}

export interface AppendTimelineHistoryTransactionChangesRequest {
  readonly transactionId: string;
  readonly changes: readonly TimelineHistoryChange[];
}

export interface CommitTimelineHistoryTransactionRequest<TState = TimelineHistoryJsonValue> {
  readonly transactionId: string;
  readonly entryId: string;
  readonly after: TimelineHistoryStatePayload<TState>;
  readonly committedAt?: number;
  readonly metadata?: Readonly<Record<string, TimelineHistoryJsonValue>>;
}

export interface CancelTimelineHistoryTransactionRequest {
  readonly transactionId: string;
  readonly reason?: string;
}

export interface UndoTimelineHistoryRequest {
  readonly expectedEntryId?: string | null;
  readonly expectedStateVersion?: number | null;
  readonly expectedTimelineVersion?: number | null;
  readonly currentChecksum?: string | null;
}

export interface RedoTimelineHistoryRequest {
  readonly expectedEntryId?: string | null;
  readonly expectedStateVersion?: number | null;
  readonly expectedTimelineVersion?: number | null;
  readonly currentChecksum?: string | null;
}

export interface CreateTimelineHistoryCheckpointRequest<TState = TimelineHistoryJsonValue> {
  readonly checkpointId: string;
  readonly label: string;
  readonly state: TimelineHistoryStatePayload<TState>;
  readonly entryId?: string | null;
  readonly protected?: boolean;
  readonly createdAt?: number;
  readonly metadata?: Readonly<Record<string, TimelineHistoryJsonValue>>;
}

export interface RestoreTimelineHistoryCheckpointRequest {
  readonly checkpointId: string;
  readonly expectedStateVersion?: number | null;
  readonly expectedTimelineVersion?: number | null;
  readonly currentChecksum?: string | null;
}

export interface RemoveTimelineHistoryCheckpointRequest {
  readonly checkpointId: string;
  readonly force?: boolean;
}

export interface TimelineUndoRedoHistorySnapshot<TState = TimelineHistoryJsonValue> {
  readonly contractVersion: typeof TIMELINE_UNDO_REDO_HISTORY_CONTRACT_VERSION;
  readonly version: number;
  readonly status: TimelineUndoRedoHistoryStatus;
  readonly configured: boolean;
  readonly configuration: TimelineUndoRedoHistoryConfiguration;
  readonly baseline: TimelineHistoryStatePayload<TState> | null;
  readonly current: TimelineHistoryStatePayload<TState> | null;
  readonly past: readonly TimelineHistoryEntry<TState>[];
  readonly future: readonly TimelineHistoryEntry<TState>[];
  readonly transaction: TimelineHistoryTransaction<TState> | null;
  readonly checkpoints: readonly TimelineHistoryCheckpoint<TState>[];
  readonly branches: readonly TimelineHistoryBranch[];
  readonly activeBranchId: string;
  readonly canUndo: boolean;
  readonly canRedo: boolean;
  readonly conflicts: readonly TimelineHistoryConflict[];
}

export type TimelineUndoRedoHistoryEventType =
  | "configured"
  | "baseline-replaced"
  | "entry-recorded"
  | "entry-merged"
  | "transaction-started"
  | "transaction-change-appended"
  | "transaction-committed"
  | "transaction-cancelled"
  | "undo-completed"
  | "redo-completed"
  | "checkpoint-created"
  | "checkpoint-restored"
  | "checkpoint-removed"
  | "history-cleared"
  | "reset"
  | "disposed";

export interface TimelineUndoRedoHistoryEvent<TState = TimelineHistoryJsonValue> {
  readonly type: TimelineUndoRedoHistoryEventType;
  readonly snapshot: TimelineUndoRedoHistorySnapshot<TState>;
}

export type TimelineUndoRedoHistoryListener<TState = TimelineHistoryJsonValue> = (
  event: TimelineUndoRedoHistoryEvent<TState>,
) => void;
