import type {
  BeginTimelineHistoryTransactionRequest,
  CommitTimelineHistoryTransactionRequest,
  TimelineHistoryChange,
  TimelineHistoryEntry,
  TimelineHistoryJsonValue,
  TimelineHistoryTransaction,
} from "../contracts/timeline-history-contracts";
import { TimelineHistoryEntryModel } from "./timeline-history-entry-model";

export class TimelineHistoryTransactionModel {
  static create<TState = TimelineHistoryJsonValue>(
    request: BeginTimelineHistoryTransactionRequest<TState>,
    branchId: string,
  ): TimelineHistoryTransaction<TState> {
    if (!request.transactionId.trim()) throw new Error("Timeline history transaction id is required.");
    return Object.freeze({
      transactionId: request.transactionId,
      label: request.label,
      operation: request.operation,
      sourceRuntime: request.sourceRuntime,
      mergeKey: request.mergeKey ?? null,
      branchId,
      startedAt: request.startedAt ?? Date.now(),
      baseline: TimelineHistoryEntryModel.cloneState(request.baseline),
      changes: Object.freeze([]),
      metadata: Object.freeze({ ...(request.metadata ?? {}) }),
    });
  }

  static append<TState>(
    transaction: TimelineHistoryTransaction<TState>,
    changes: readonly TimelineHistoryChange[],
  ): TimelineHistoryTransaction<TState> {
    if (changes.length === 0) return transaction;
    return Object.freeze({
      ...transaction,
      changes: TimelineHistoryEntryModel.normalizeChanges([...transaction.changes, ...changes]),
    });
  }

  static commit<TState = TimelineHistoryJsonValue>(
    transaction: TimelineHistoryTransaction<TState>,
    request: CommitTimelineHistoryTransactionRequest<TState>,
    sequence: number,
  ): TimelineHistoryEntry<TState> {
    if (request.transactionId !== transaction.transactionId) throw new Error("Timeline history transaction id mismatch.");
    if (transaction.changes.length === 0) throw new Error("Timeline history transaction cannot commit without changes.");
    return TimelineHistoryEntryModel.create(
      {
        entryId: request.entryId,
        operation: transaction.operation,
        label: transaction.label,
        sourceRuntime: transaction.sourceRuntime,
        before: transaction.baseline,
        after: request.after,
        changes: transaction.changes,
        mergeKey: transaction.mergeKey,
        createdAt: request.committedAt,
        metadata: Object.freeze({ ...transaction.metadata, ...(request.metadata ?? {}) }),
      },
      transaction.branchId,
      sequence,
      transaction.transactionId,
    );
  }
}
