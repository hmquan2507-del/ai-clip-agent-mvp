import {
  TIMELINE_UNDO_REDO_HISTORY_CONTRACT_VERSION,
  type AppendTimelineHistoryTransactionChangeRequest,
  type AppendTimelineHistoryTransactionChangesRequest,
  type BeginTimelineHistoryTransactionRequest,
  type CancelTimelineHistoryTransactionRequest,
  type CommitTimelineHistoryTransactionRequest,
  type RecordTimelineHistoryEntryRequest,
  type RedoTimelineHistoryRequest,
  type ReplaceTimelineHistoryBaselineRequest,
  type TimelineHistoryBranch,
  type TimelineHistoryConflict,
  type TimelineHistoryEntry,
  type TimelineHistoryJsonValue,
  type TimelineHistoryPeekResult,
  type TimelineHistoryRecordResult,
  type TimelineHistoryRestoreResult,
  type TimelineHistoryStatePayload,
  type TimelineHistoryTransaction,
  type TimelineHistoryTransactionResult,
  type TimelineUndoRedoHistoryConfiguration,
  type TimelineUndoRedoHistoryEvent,
  type TimelineUndoRedoHistoryEventType,
  type TimelineUndoRedoHistoryListener,
  type TimelineUndoRedoHistorySnapshot,
  type TimelineUndoRedoHistoryStatus,
  type UndoTimelineHistoryRequest,
} from "../contracts/timeline-history-contracts";
import { TimelineHistoryEntryModel } from "./timeline-history-entry-model";
import { TimelineHistoryMergeModel } from "./timeline-history-merge-model";
import { TimelineHistoryTransactionModel } from "./timeline-history-transaction-model";

const DEFAULT_CONFIGURATION: Required<TimelineUndoRedoHistoryConfiguration> = Object.freeze({
  maxEntries: 200,
  maxCheckpoints: 20,
  mergeWindowMs: 750,
  preserveBranches: true,
  recordSelectionChanges: false,
  protectCheckpointEntries: true,
  validateChecksums: true,
  requireContiguousStateVersions: true,
  requireContiguousTimelineVersions: true,
});

function conflict(
  code: TimelineHistoryConflict["code"],
  message: string,
  extra: Partial<TimelineHistoryConflict> = {},
): TimelineHistoryConflict {
  return Object.freeze({ code, message, blocking: true, ...extra });
}

function immutableBranch(branch: TimelineHistoryBranch): TimelineHistoryBranch {
  return Object.freeze({ ...branch, entryIds: Object.freeze([...branch.entryIds]) });
}

export class TimelineUndoRedoHistoryRuntime<TState = TimelineHistoryJsonValue> {
  private configuration: Required<TimelineUndoRedoHistoryConfiguration> = DEFAULT_CONFIGURATION;
  private configured = false;
  private version = 0;
  private status: TimelineUndoRedoHistoryStatus = "idle";
  private baseline: TimelineHistoryStatePayload<TState> | null = null;
  private current: TimelineHistoryStatePayload<TState> | null = null;
  private past: TimelineHistoryEntry<TState>[] = [];
  private future: TimelineHistoryEntry<TState>[] = [];
  private transaction: TimelineHistoryTransaction<TState> | null = null;
  private checkpoints: TimelineUndoRedoHistorySnapshot<TState>["checkpoints"] = Object.freeze([]);
  private branches = new Map<string, TimelineHistoryBranch>();
  private activeBranchId = "main";
  private conflicts: readonly TimelineHistoryConflict[] = Object.freeze([]);
  private listeners = new Set<TimelineUndoRedoHistoryListener<TState>>();
  private sequence = 0;
  private branchSequence = 0;

  constructor(configuration?: TimelineUndoRedoHistoryConfiguration) {
    this.branches.set("main", immutableBranch({
      branchId: "main",
      parentBranchId: null,
      forkedFromEntryId: null,
      createdAt: Date.now(),
      entryIds: Object.freeze([]),
      active: true,
    }));
    if (configuration) this.configure(configuration);
  }

  configure(configuration: TimelineUndoRedoHistoryConfiguration = {}): TimelineUndoRedoHistorySnapshot<TState> {
    this.assertNotDisposed();
    const next = { ...DEFAULT_CONFIGURATION, ...configuration };
    const invalid =
      !Number.isInteger(next.maxEntries) || next.maxEntries < 1 ||
      !Number.isInteger(next.maxCheckpoints) || next.maxCheckpoints < 0 ||
      !Number.isFinite(next.mergeWindowMs) || next.mergeWindowMs < 0;
    if (invalid) {
      this.setConflicts([conflict("invalid-configuration", "Timeline history configuration is invalid.")]);
      throw new Error("Timeline history configuration is invalid.");
    }
    this.configuration = Object.freeze(next);
    this.configured = true;
    this.status = this.transaction ? "transaction-open" : "idle";
    this.bump("configured");
    return this.getSnapshot();
  }

  replaceBaseline(request: ReplaceTimelineHistoryBaselineRequest<TState>): TimelineUndoRedoHistorySnapshot<TState> {
    this.assertReady();
    this.assertNoOpenTransaction();
    this.baseline = TimelineHistoryEntryModel.cloneState(request.state);
    this.current = TimelineHistoryEntryModel.cloneState(request.state);
    if (request.branchId?.trim()) this.activateOrCreateBranch(request.branchId, null);
    if (request.clearHistory ?? true) {
      this.past = [];
      this.future = [];
      this.sequence = 0;
      this.replaceBranchEntries(this.activeBranchId, []);
    }
    if (request.clearCheckpoints) this.checkpoints = Object.freeze([]);
    this.status = "idle";
    this.setConflicts([]);
    this.bump("baseline-replaced");
    return this.getSnapshot();
  }

  record(request: RecordTimelineHistoryEntryRequest<TState>): TimelineHistoryRecordResult<TState> {
    this.assertReady();
    this.assertNoOpenTransaction();
    this.status = "recording";
    const validation = this.validateRecordRequest(request);
    if (validation.length > 0) return this.recordFailure(validation);
    if (request.operation === "selection-change" && !this.configuration.recordSelectionChanges) {
      this.status = "idle";
      return Object.freeze({
        recorded: false,
        merged: false,
        entry: null,
        evictedEntryIds: Object.freeze([]),
        clearedFutureEntryIds: Object.freeze([]),
        branch: null,
        conflicts: Object.freeze([]),
      });
    }

    const clearedFutureEntryIds = this.future.map((entry) => entry.entryId);
    let branch: TimelineHistoryBranch | null = null;
    if (this.future.length > 0 && this.configuration.preserveBranches) {
      branch = this.forkFromFuture();
    }
    this.future = [];

    const incoming = TimelineHistoryEntryModel.create(request, this.activeBranchId, ++this.sequence);
    const previous = this.past.at(-1) ?? null;
    if (previous) {
      const decision = TimelineHistoryMergeModel.decide(previous, incoming, this.configuration.mergeWindowMs);
      if (decision.mergeable && decision.mergedEntry) {
        this.past[this.past.length - 1] = decision.mergedEntry;
        this.current = decision.mergedEntry.after;
        this.replaceLastBranchEntry(previous.entryId, decision.mergedEntry.entryId);
        this.status = "idle";
        this.setConflicts([]);
        this.bump("entry-merged");
        return Object.freeze({
          recorded: true,
          merged: true,
          entry: decision.mergedEntry,
          evictedEntryIds: Object.freeze([]),
          clearedFutureEntryIds: Object.freeze(clearedFutureEntryIds),
          branch,
          conflicts: Object.freeze([]),
        });
      }
    }

    this.past.push(incoming);
    this.current = incoming.after;
    this.appendBranchEntry(incoming.entryId);
    const evictedEntryIds = this.enforceEntryCapacity();
    this.status = "idle";
    this.setConflicts([]);
    this.bump("entry-recorded");
    return Object.freeze({
      recorded: true,
      merged: false,
      entry: incoming,
      evictedEntryIds: Object.freeze(evictedEntryIds),
      clearedFutureEntryIds: Object.freeze(clearedFutureEntryIds),
      branch,
      conflicts: Object.freeze([]),
    });
  }

  beginTransaction(request: BeginTimelineHistoryTransactionRequest<TState>): TimelineHistoryTransaction<TState> {
    this.assertReady();
    if (this.transaction) throw new Error("A timeline history transaction is already open.");
    this.transaction = TimelineHistoryTransactionModel.create(request, this.activeBranchId);
    this.status = "transaction-open";
    this.setConflicts([]);
    this.bump("transaction-started");
    return this.transaction;
  }

  appendTransactionChange(request: AppendTimelineHistoryTransactionChangeRequest): TimelineHistoryTransaction<TState> {
    return this.appendTransactionChanges({ transactionId: request.transactionId, changes: [request.change] });
  }

  appendTransactionChanges(request: AppendTimelineHistoryTransactionChangesRequest): TimelineHistoryTransaction<TState> {
    this.assertReady();
    const active = this.requireTransaction(request.transactionId);
    this.transaction = TimelineHistoryTransactionModel.append(active, request.changes);
    this.bump("transaction-change-appended");
    return this.transaction;
  }

  commitTransaction(request: CommitTimelineHistoryTransactionRequest<TState>): TimelineHistoryTransactionResult<TState> {
    this.assertReady();
    const active = this.requireTransaction(request.transactionId);
    if (active.changes.length === 0) {
      const conflicts = [conflict("empty-transaction", "Timeline history transaction has no changes.", { transactionId: active.transactionId })];
      this.setConflicts(conflicts);
      return Object.freeze({ committed: false, transaction: active, recordResult: null, conflicts: Object.freeze(conflicts) });
    }
    const entryRequest: RecordTimelineHistoryEntryRequest<TState> = {
      entryId: request.entryId,
      operation: active.operation,
      label: active.label,
      sourceRuntime: active.sourceRuntime,
      before: active.baseline,
      after: request.after,
      changes: active.changes,
      mergeKey: active.mergeKey,
      createdAt: request.committedAt,
      metadata: Object.freeze({ ...active.metadata, ...(request.metadata ?? {}) }),
    };
    this.transaction = null;
    this.status = "idle";
    const recordResult = this.record(entryRequest);
    this.bump("transaction-committed");
    return Object.freeze({
      committed: recordResult.recorded,
      transaction: active,
      recordResult,
      conflicts: recordResult.conflicts,
    });
  }

  cancelTransaction(request: CancelTimelineHistoryTransactionRequest): TimelineHistoryTransaction<TState> {
    this.assertReady();
    const active = this.requireTransaction(request.transactionId);
    this.transaction = null;
    this.status = "idle";
    this.setConflicts([]);
    this.bump("transaction-cancelled");
    return active;
  }

  peekUndo(): TimelineHistoryPeekResult<TState> {
    return this.peek(this.past.at(-1) ?? null, "undo-unavailable", "No timeline history entry is available to undo.");
  }

  peekRedo(): TimelineHistoryPeekResult<TState> {
    return this.peek(this.future.at(-1) ?? null, "redo-unavailable", "No timeline history entry is available to redo.");
  }

  undo(request: UndoTimelineHistoryRequest = {}): TimelineHistoryRestoreResult<TState> {
    this.assertReady();
    this.assertNoOpenTransaction();
    const entry = this.past.at(-1) ?? null;
    const validation = this.validateRestore(entry, request, "undo");
    if (validation.length > 0) return this.restoreFailure("undo", validation);
    this.status = "restoring";
    this.past.pop();
    this.future.push(entry!);
    this.current = entry!.before;
    this.status = "idle";
    this.setConflicts([]);
    this.bump("undo-completed");
    return Object.freeze({ restored: true, direction: "undo", entry, checkpoint: null, state: this.current, conflicts: Object.freeze([]) });
  }

  redo(request: RedoTimelineHistoryRequest = {}): TimelineHistoryRestoreResult<TState> {
    this.assertReady();
    this.assertNoOpenTransaction();
    const entry = this.future.at(-1) ?? null;
    const validation = this.validateRestore(entry, request, "redo");
    if (validation.length > 0) return this.restoreFailure("redo", validation);
    this.status = "restoring";
    this.future.pop();
    this.past.push(entry!);
    this.current = entry!.after;
    this.status = "idle";
    this.setConflicts([]);
    this.bump("redo-completed");
    return Object.freeze({ restored: true, direction: "redo", entry, checkpoint: null, state: this.current, conflicts: Object.freeze([]) });
  }

  clearHistory(): TimelineUndoRedoHistorySnapshot<TState> {
    this.assertReady();
    this.assertNoOpenTransaction();
    this.past = [];
    this.future = [];
    this.sequence = 0;
    this.replaceBranchEntries(this.activeBranchId, []);
    this.setConflicts([]);
    this.bump("history-cleared");
    return this.getSnapshot();
  }

  reset(): TimelineUndoRedoHistorySnapshot<TState> {
    this.assertNotDisposed();
    this.baseline = null;
    this.current = null;
    this.past = [];
    this.future = [];
    this.transaction = null;
    this.checkpoints = Object.freeze([]);
    this.sequence = 0;
    this.branchSequence = 0;
    this.activeBranchId = "main";
    this.branches.clear();
    this.branches.set("main", immutableBranch({ branchId: "main", parentBranchId: null, forkedFromEntryId: null, createdAt: Date.now(), entryIds: Object.freeze([]), active: true }));
    this.status = "idle";
    this.setConflicts([]);
    this.bump("reset");
    return this.getSnapshot();
  }

  subscribe(listener: TimelineUndoRedoHistoryListener<TState>): () => void {
    this.assertNotDisposed();
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  getSnapshot(): TimelineUndoRedoHistorySnapshot<TState> {
    return Object.freeze({
      contractVersion: TIMELINE_UNDO_REDO_HISTORY_CONTRACT_VERSION,
      version: this.version,
      status: this.status,
      configured: this.configured,
      configuration: this.configuration,
      baseline: this.baseline,
      current: this.current,
      past: Object.freeze([...this.past]),
      future: Object.freeze([...this.future]),
      transaction: this.transaction,
      checkpoints: this.checkpoints,
      branches: Object.freeze([...this.branches.values()].map(immutableBranch)),
      activeBranchId: this.activeBranchId,
      canUndo: this.past.length > 0 && !this.transaction && this.status !== "disposed",
      canRedo: this.future.length > 0 && !this.transaction && this.status !== "disposed",
      conflicts: this.conflicts,
    });
  }

  dispose(): void {
    if (this.status === "disposed") return;
    this.status = "disposed";
    this.transaction = null;
    this.bump("disposed");
    this.listeners.clear();
  }

  private validateRecordRequest(request: RecordTimelineHistoryEntryRequest<TState>): TimelineHistoryConflict[] {
    const conflicts: TimelineHistoryConflict[] = [];
    if (!request.entryId.trim()) conflicts.push(conflict("missing-entry-id", "Timeline history entry id is required."));
    if (this.hasEntryId(request.entryId)) conflicts.push(conflict("duplicate-entry-id", "Timeline history entry id already exists.", { entryId: request.entryId }));
    if (request.changes.length === 0) conflicts.push(conflict("empty-change-set", "Timeline history entry must contain at least one change.", { entryId: request.entryId }));
    if (!this.validPayload(request.before) || !this.validPayload(request.after)) conflicts.push(conflict("invalid-state-payload", "Timeline history state payload is invalid.", { entryId: request.entryId }));
    if (this.current) {
      if (this.configuration.requireContiguousStateVersions && request.before.stateVersion !== this.current.stateVersion) {
        conflicts.push(conflict("state-version-conflict", "Before state version does not match current state version.", { entryId: request.entryId, expectedVersion: this.current.stateVersion, actualVersion: request.before.stateVersion }));
      }
      if (this.configuration.requireContiguousTimelineVersions && request.before.timelineVersion !== this.current.timelineVersion) {
        conflicts.push(conflict("timeline-version-conflict", "Before timeline version does not match current timeline version.", { entryId: request.entryId, expectedVersion: this.current.timelineVersion, actualVersion: request.before.timelineVersion }));
      }
      if (this.configuration.validateChecksums && request.before.checksum !== this.current.checksum) {
        conflicts.push(conflict("checksum-mismatch", "Before checksum does not match current checksum.", { entryId: request.entryId }));
      }
    }
    return conflicts;
  }

  private validateRestore(
    entry: TimelineHistoryEntry<TState> | null,
    request: UndoTimelineHistoryRequest | RedoTimelineHistoryRequest,
    direction: "undo" | "redo",
  ): TimelineHistoryConflict[] {
    if (!entry) return [conflict(direction === "undo" ? "undo-unavailable" : "redo-unavailable", `No timeline history entry is available to ${direction}.`)];
    const conflicts: TimelineHistoryConflict[] = [];
    if (request.expectedEntryId != null && request.expectedEntryId !== entry.entryId) conflicts.push(conflict("expected-entry-mismatch", "Expected timeline history entry does not match.", { entryId: entry.entryId }));
    if (this.current && request.expectedStateVersion != null && request.expectedStateVersion !== this.current.stateVersion) conflicts.push(conflict("state-version-conflict", "Expected state version does not match current state.", { entryId: entry.entryId, expectedVersion: request.expectedStateVersion, actualVersion: this.current.stateVersion }));
    if (this.current && request.expectedTimelineVersion != null && request.expectedTimelineVersion !== this.current.timelineVersion) conflicts.push(conflict("timeline-version-conflict", "Expected timeline version does not match current timeline.", { entryId: entry.entryId, expectedVersion: request.expectedTimelineVersion, actualVersion: this.current.timelineVersion }));
    if (this.current && this.configuration.validateChecksums && request.currentChecksum != null && request.currentChecksum !== this.current.checksum) conflicts.push(conflict("checksum-mismatch", "Current checksum does not match restore request.", { entryId: entry.entryId }));
    return conflicts;
  }

  private peek(entry: TimelineHistoryEntry<TState> | null, code: "undo-unavailable" | "redo-unavailable", message: string): TimelineHistoryPeekResult<TState> {
    if (entry) return Object.freeze({ available: true, entry, conflicts: Object.freeze([]) });
    return Object.freeze({ available: false, entry: null, conflicts: Object.freeze([conflict(code, message)]) });
  }

  private recordFailure(conflicts: TimelineHistoryConflict[]): TimelineHistoryRecordResult<TState> {
    this.status = "blocked";
    this.setConflicts(conflicts);
    return Object.freeze({ recorded: false, merged: false, entry: null, evictedEntryIds: Object.freeze([]), clearedFutureEntryIds: Object.freeze([]), branch: null, conflicts: Object.freeze(conflicts) });
  }

  private restoreFailure(direction: "undo" | "redo", conflicts: TimelineHistoryConflict[]): TimelineHistoryRestoreResult<TState> {
    this.status = "blocked";
    this.setConflicts(conflicts);
    return Object.freeze({ restored: false, direction, entry: null, checkpoint: null, state: null, conflicts: Object.freeze(conflicts) });
  }

  private validPayload(payload: TimelineHistoryStatePayload<TState>): boolean {
    return Number.isInteger(payload.stateVersion) && payload.stateVersion >= 0 && Number.isInteger(payload.timelineVersion) && payload.timelineVersion >= 0 && typeof payload.checksum === "string" && payload.checksum.length > 0 && Number.isFinite(payload.capturedAt);
  }

  private requireTransaction(transactionId: string): TimelineHistoryTransaction<TState> {
    if (!this.transaction) throw new Error("No timeline history transaction is open.");
    if (this.transaction.transactionId !== transactionId) throw new Error("Timeline history transaction id mismatch.");
    return this.transaction;
  }

  private assertReady(): void {
    this.assertNotDisposed();
    if (!this.configured) {
      this.setConflicts([conflict("not-configured", "Timeline undo/redo history runtime is not configured.")]);
      throw new Error("Timeline undo/redo history runtime is not configured.");
    }
  }

  private assertNoOpenTransaction(): void {
    if (this.transaction) throw new Error("Timeline history operation is blocked while a transaction is open.");
  }

  private assertNotDisposed(): void {
    if (this.status === "disposed") throw new Error("Timeline undo/redo history runtime is disposed.");
  }

  private hasEntryId(entryId: string): boolean {
    return this.past.some((entry) => entry.entryId === entryId) || this.future.some((entry) => entry.entryId === entryId);
  }

  private enforceEntryCapacity(): string[] {
    const evicted: string[] = [];
    while (this.past.length > this.configuration.maxEntries) {
      const removed = this.past.shift();
      if (removed) evicted.push(removed.entryId);
    }
    return evicted;
  }

  private appendBranchEntry(entryId: string): void {
    const branch = this.branches.get(this.activeBranchId)!;
    this.branches.set(this.activeBranchId, immutableBranch({ ...branch, entryIds: [...branch.entryIds, entryId] }));
  }

  private replaceLastBranchEntry(previousEntryId: string, nextEntryId: string): void {
    const branch = this.branches.get(this.activeBranchId)!;
    const entries = [...branch.entryIds];
    const index = entries.lastIndexOf(previousEntryId);
    if (index >= 0) entries[index] = nextEntryId;
    this.branches.set(this.activeBranchId, immutableBranch({ ...branch, entryIds: entries }));
  }

  private replaceBranchEntries(branchId: string, entryIds: readonly string[]): void {
    const branch = this.branches.get(branchId);
    if (branch) this.branches.set(branchId, immutableBranch({ ...branch, entryIds }));
  }

  private forkFromFuture(): TimelineHistoryBranch {
    const parent = this.activeBranchId;
    const branchId = `branch-${++this.branchSequence}`;
    const forkedFromEntryId = this.past.at(-1)?.entryId ?? null;
    const parentBranch = this.branches.get(parent)!;
    this.branches.set(parent, immutableBranch({ ...parentBranch, active: false }));
    const branch = immutableBranch({ branchId, parentBranchId: parent, forkedFromEntryId, createdAt: Date.now(), entryIds: Object.freeze(this.past.map((entry) => entry.entryId)), active: true });
    this.branches.set(branchId, branch);
    this.activeBranchId = branchId;
    return branch;
  }

  private activateOrCreateBranch(branchId: string, forkedFromEntryId: string | null): void {
    for (const [id, branch] of this.branches) this.branches.set(id, immutableBranch({ ...branch, active: id === branchId }));
    if (!this.branches.has(branchId)) this.branches.set(branchId, immutableBranch({ branchId, parentBranchId: this.activeBranchId, forkedFromEntryId, createdAt: Date.now(), entryIds: Object.freeze([]), active: true }));
    this.activeBranchId = branchId;
  }

  private setConflicts(conflicts: readonly TimelineHistoryConflict[]): void {
    this.conflicts = Object.freeze([...conflicts]);
  }

  private bump(type: TimelineUndoRedoHistoryEventType): void {
    this.version += 1;
    const event: TimelineUndoRedoHistoryEvent<TState> = Object.freeze({ type, snapshot: this.getSnapshot() });
    for (const listener of [...this.listeners]) listener(event);
  }
}
