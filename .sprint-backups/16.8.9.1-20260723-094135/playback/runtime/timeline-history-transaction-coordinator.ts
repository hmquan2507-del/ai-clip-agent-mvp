import type {
  BeginTimelineHistoryTransactionRequest,
  CommitTimelineHistoryTransactionRequest,
  TimelineHistoryChange,
  TimelineHistoryJsonValue,
  TimelineHistoryStatePayload,
  TimelineHistoryTransaction,
  TimelineHistoryTransactionResult,
} from "../contracts/timeline-history-contracts";
import { TimelineUndoRedoHistoryRuntime } from "./timeline-undo-redo-history-runtime";

export interface TimelineHistoryTransactionSavepoint {
  readonly savepointId: string;
  readonly transactionId: string;
  readonly changeCount: number;
  readonly createdAt: number;
}

export interface TimelineHistoryTransactionCoordinatorSnapshot<TState = TimelineHistoryJsonValue> {
  readonly transaction: TimelineHistoryTransaction<TState> | null;
  readonly savepoints: readonly TimelineHistoryTransactionSavepoint[];
  readonly rollbackCount: number;
}

export class TimelineHistoryTransactionCoordinator<TState = TimelineHistoryJsonValue> {
  private savepoints: TimelineHistoryTransactionSavepoint[] = [];
  private rollbackCount = 0;

  constructor(private readonly runtime: TimelineUndoRedoHistoryRuntime<TState>) {}

  begin(request: BeginTimelineHistoryTransactionRequest<TState>): TimelineHistoryTransaction<TState> {
    this.savepoints = [];
    return this.runtime.beginTransaction(request);
  }

  append(transactionId: string, change: TimelineHistoryChange): TimelineHistoryTransaction<TState> {
    return this.runtime.appendTransactionChange({ transactionId, change });
  }

  appendMany(transactionId: string, changes: readonly TimelineHistoryChange[]): TimelineHistoryTransaction<TState> {
    return this.runtime.appendTransactionChanges({ transactionId, changes });
  }

  createSavepoint(savepointId: string): TimelineHistoryTransactionSavepoint {
    if (!savepointId.trim()) throw new Error("Timeline history savepoint id is required.");
    const transaction = this.requireTransaction();
    if (this.savepoints.some((savepoint) => savepoint.savepointId === savepointId)) {
      throw new Error(`Timeline history savepoint ${savepointId} already exists.`);
    }
    const savepoint = Object.freeze({
      savepointId,
      transactionId: transaction.transactionId,
      changeCount: transaction.changes.length,
      createdAt: Date.now(),
    });
    this.savepoints.push(savepoint);
    return savepoint;
  }

  rollbackToSavepoint(savepointId: string): TimelineHistoryTransaction<TState> {
    const transaction = this.requireTransaction();
    const savepoint = this.savepoints.find((candidate) => candidate.savepointId === savepointId);
    if (!savepoint || savepoint.transactionId !== transaction.transactionId) {
      throw new Error(`Timeline history savepoint ${savepointId} was not found.`);
    }
    this.runtime.cancelTransaction({ transactionId: transaction.transactionId, reason: `rollback:${savepointId}` });
    let restored = this.runtime.beginTransaction({
      transactionId: transaction.transactionId,
      operation: transaction.operation,
      label: transaction.label,
      sourceRuntime: transaction.sourceRuntime,
      baseline: transaction.baseline,
      mergeKey: transaction.mergeKey,
      startedAt: transaction.startedAt,
      metadata: transaction.metadata,
    });
    if (savepoint.changeCount > 0) {
      restored = this.runtime.appendTransactionChanges({
        transactionId: transaction.transactionId,
        changes: transaction.changes.slice(0, savepoint.changeCount),
      });
    }
    const savepointIndex = this.savepoints.findIndex((candidate) => candidate.savepointId === savepointId);
    this.savepoints = this.savepoints.slice(0, savepointIndex + 1);
    this.rollbackCount += 1;
    return restored;
  }

  rollback(reason = "coordinator-rollback"): TimelineHistoryTransaction<TState> {
    const transaction = this.requireTransaction();
    const cancelled = this.runtime.cancelTransaction({ transactionId: transaction.transactionId, reason });
    this.savepoints = [];
    this.rollbackCount += 1;
    return cancelled;
  }

  commit(
    transactionId: string,
    entryId: string,
    after: TimelineHistoryStatePayload<TState>,
    metadata?: CommitTimelineHistoryTransactionRequest<TState>["metadata"],
  ): TimelineHistoryTransactionResult<TState> {
    const result = this.runtime.commitTransaction({ transactionId, entryId, after, metadata });
    if (result.committed) this.savepoints = [];
    return result;
  }

  run<TResult>(
    request: BeginTimelineHistoryTransactionRequest<TState>,
    operation: (coordinator: TimelineHistoryTransactionCoordinator<TState>) => TResult,
    complete: (result: TResult) => { readonly entryId: string; readonly after: TimelineHistoryStatePayload<TState> },
  ): TimelineHistoryTransactionResult<TState> {
    this.begin(request);
    try {
      const result = operation(this);
      const completion = complete(result);
      return this.commit(request.transactionId, completion.entryId, completion.after);
    } catch (error) {
      const snapshot = this.runtime.getSnapshot();
      if (snapshot.transaction?.transactionId === request.transactionId) this.rollback("coordinator-exception");
      throw error;
    }
  }

  getSnapshot(): TimelineHistoryTransactionCoordinatorSnapshot<TState> {
    return Object.freeze({
      transaction: this.runtime.getSnapshot().transaction,
      savepoints: Object.freeze([...this.savepoints]),
      rollbackCount: this.rollbackCount,
    });
  }

  private requireTransaction(): TimelineHistoryTransaction<TState> {
    const transaction = this.runtime.getSnapshot().transaction;
    if (!transaction) throw new Error("No timeline history transaction is open.");
    return transaction;
  }
}
