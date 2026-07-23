import type {
  TimelineHistoryChange,
  TimelineHistoryEntry,
  TimelineHistoryJsonValue,
} from "../contracts/timeline-history-contracts";
import { TimelineHistoryEntryModel } from "./timeline-history-entry-model";

export type TimelineHistoryMergePolicy = "reject" | "prefer-source" | "prefer-target" | "latest-wins";

export interface TimelineHistoryMergeConflict {
  readonly identity: string;
  readonly source: TimelineHistoryChange;
  readonly target: TimelineHistoryChange;
  readonly reason: "divergent-after-value" | "incompatible-kind";
}

export interface TimelineHistoryMergePlan<TState = TimelineHistoryJsonValue> {
  readonly mergeable: boolean;
  readonly policy: TimelineHistoryMergePolicy;
  readonly sourceEntryId: string;
  readonly targetEntryId: string;
  readonly mergedEntry: TimelineHistoryEntry<TState> | null;
  readonly conflicts: readonly TimelineHistoryMergeConflict[];
  readonly appliedChangeIds: readonly string[];
  readonly reason: string;
}

const identity = (change: TimelineHistoryChange): string =>
  [change.entityType, change.entityId, change.path ?? ""].join("\u0000");

const same = (left: unknown, right: unknown): boolean => JSON.stringify(left) === JSON.stringify(right);

export class TimelineHistoryMergeStrategy {
  static merge<TState = TimelineHistoryJsonValue>(
    target: TimelineHistoryEntry<TState>,
    source: TimelineHistoryEntry<TState>,
    policy: TimelineHistoryMergePolicy = "reject",
  ): TimelineHistoryMergePlan<TState> {
    const targetChanges = new Map(target.changes.map((change) => [identity(change), change]));
    const sourceChanges = new Map(source.changes.map((change) => [identity(change), change]));
    const merged = new Map(targetChanges);
    const conflicts: TimelineHistoryMergeConflict[] = [];

    for (const [key, sourceChange] of sourceChanges) {
      const targetChange = targetChanges.get(key);
      if (!targetChange) {
        merged.set(key, sourceChange);
        continue;
      }
      if (targetChange.kind !== sourceChange.kind) {
        conflicts.push(Object.freeze({ identity: key, source: sourceChange, target: targetChange, reason: "incompatible-kind" }));
      } else if (!same(targetChange.after, sourceChange.after)) {
        conflicts.push(Object.freeze({ identity: key, source: sourceChange, target: targetChange, reason: "divergent-after-value" }));
      } else {
        merged.set(key, Object.freeze({ ...sourceChange, changeId: targetChange.changeId, before: targetChange.before }));
      }
    }

    if (conflicts.length > 0 && policy === "reject") {
      return Object.freeze({
        mergeable: false,
        policy,
        sourceEntryId: source.entryId,
        targetEntryId: target.entryId,
        mergedEntry: null,
        conflicts: Object.freeze(conflicts),
        appliedChangeIds: Object.freeze([]),
        reason: "unresolved-conflicts",
      });
    }

    for (const conflict of conflicts) {
      const selected = policy === "prefer-source"
        ? conflict.source
        : policy === "prefer-target"
          ? conflict.target
          : source.createdAt >= target.createdAt
            ? conflict.source
            : conflict.target;
      merged.set(conflict.identity, selected);
    }

    const mergedEntry = TimelineHistoryEntryModel.replace(target, {
      after: source.after,
      changes: [...merged.values()],
      createdAt: Math.max(target.createdAt, source.createdAt),
      metadata: Object.freeze({ ...target.metadata, ...source.metadata, mergePolicy: policy }),
    });
    return Object.freeze({
      mergeable: true,
      policy,
      sourceEntryId: source.entryId,
      targetEntryId: target.entryId,
      mergedEntry,
      conflicts: Object.freeze(conflicts),
      appliedChangeIds: Object.freeze(mergedEntry.changes.map((change) => change.changeId)),
      reason: conflicts.length > 0 ? "conflicts-resolved" : "merged-without-conflicts",
    });
  }
}
