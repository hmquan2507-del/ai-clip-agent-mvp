import type {
  TimelineHistoryChange,
  TimelineHistoryEntry,
  TimelineHistoryJsonValue,
  TimelineHistoryMergeDecision,
} from "../contracts/timeline-history-contracts";
import { TimelineHistoryEntryModel } from "./timeline-history-entry-model";

const identity = (change: TimelineHistoryChange): string =>
  [change.entityType, change.entityId, change.path ?? "", change.kind].join("\u0000");

export class TimelineHistoryMergeModel {
  static decide<TState = TimelineHistoryJsonValue>(
    previous: TimelineHistoryEntry<TState>,
    incoming: TimelineHistoryEntry<TState>,
    mergeWindowMs: number,
  ): TimelineHistoryMergeDecision<TState> {
    const blocked = (reason: string): TimelineHistoryMergeDecision<TState> =>
      Object.freeze({ mergeable: false, reason, mergedEntry: null });
    if (!Number.isFinite(mergeWindowMs) || mergeWindowMs < 0) return blocked("invalid-merge-window");
    if (!previous.mergeKey || previous.mergeKey !== incoming.mergeKey) return blocked("merge-key-mismatch");
    if (previous.operation !== incoming.operation) return blocked("operation-mismatch");
    if (previous.sourceRuntime !== incoming.sourceRuntime) return blocked("source-runtime-mismatch");
    if (previous.branchId !== incoming.branchId) return blocked("branch-mismatch");
    if (incoming.createdAt - previous.createdAt > mergeWindowMs || incoming.createdAt < previous.createdAt) return blocked("outside-merge-window");
    if (previous.after.stateVersion !== incoming.before.stateVersion) return blocked("state-version-not-contiguous");
    if (previous.after.timelineVersion !== incoming.before.timelineVersion) return blocked("timeline-version-not-contiguous");
    if (previous.after.checksum !== incoming.before.checksum) return blocked("checksum-not-contiguous");

    const merged = new Map<string, TimelineHistoryChange>();
    for (const change of previous.changes) merged.set(identity(change), change);
    for (const change of incoming.changes) {
      const prior = merged.get(identity(change));
      merged.set(
        identity(change),
        prior
          ? Object.freeze({ ...change, changeId: prior.changeId, before: prior.before })
          : change,
      );
    }
    const mergedEntry = TimelineHistoryEntryModel.replace(previous, {
      after: incoming.after,
      changes: [...merged.values()],
      createdAt: incoming.createdAt,
      metadata: Object.freeze({ ...previous.metadata, ...incoming.metadata }),
    });
    return Object.freeze({ mergeable: true, reason: "compatible", mergedEntry });
  }
}
