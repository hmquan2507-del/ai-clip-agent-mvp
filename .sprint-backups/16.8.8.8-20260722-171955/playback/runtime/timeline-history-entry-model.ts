import type {
  RecordTimelineHistoryEntryRequest,
  TimelineHistoryChange,
  TimelineHistoryEntry,
  TimelineHistoryJsonValue,
  TimelineHistoryStatePayload,
} from "../contracts/timeline-history-contracts";

function cloneValue<T>(value: T): T {
  if (Array.isArray(value)) return value.map((item) => cloneValue(item)) as T;
  if (value !== null && typeof value === "object") {
    const result: Record<string, unknown> = {};
    for (const [key, child] of Object.entries(value as Record<string, unknown>)) result[key] = cloneValue(child);
    return result as T;
  }
  return value;
}

function deepFreeze<T>(value: T): T {
  if (value !== null && typeof value === "object" && !Object.isFrozen(value)) {
    Object.freeze(value);
    for (const child of Object.values(value as Record<string, unknown>)) deepFreeze(child);
  }
  return value;
}

const changeKey = (change: TimelineHistoryChange): string =>
  [change.entityType, change.entityId, change.path ?? "", change.kind, change.changeId].join("\u0000");

export class TimelineHistoryEntryModel {
  static cloneState<TState>(payload: TimelineHistoryStatePayload<TState>): TimelineHistoryStatePayload<TState> {
    return deepFreeze({
      state: cloneValue(payload.state),
      stateVersion: payload.stateVersion,
      timelineVersion: payload.timelineVersion,
      checksum: payload.checksum,
      capturedAt: payload.capturedAt,
    });
  }

  static normalizeChanges(changes: readonly TimelineHistoryChange[]): readonly TimelineHistoryChange[] {
    const normalized = changes.map((change) =>
      deepFreeze({
        ...change,
        before: cloneValue(change.before),
        after: cloneValue(change.after),
        metadata: deepFreeze(cloneValue(change.metadata ?? {})),
      }),
    );
    normalized.sort((left, right) => changeKey(left).localeCompare(changeKey(right)));
    return Object.freeze(normalized);
  }

  static create<TState = TimelineHistoryJsonValue>(
    request: RecordTimelineHistoryEntryRequest<TState>,
    branchId: string,
    sequence: number,
    transactionId: string | null = null,
  ): TimelineHistoryEntry<TState> {
    if (!request.entryId.trim()) throw new Error("Timeline history entry id is required.");
    if (!branchId.trim()) throw new Error("Timeline history branch id is required.");
    if (!Number.isInteger(sequence) || sequence < 1) throw new Error("Timeline history sequence must be a positive integer.");
    return deepFreeze({
      entryId: request.entryId,
      operation: request.operation,
      label: request.label,
      sourceRuntime: request.sourceRuntime,
      mergeKey: request.mergeKey ?? null,
      transactionId,
      branchId,
      sequence,
      before: this.cloneState(request.before),
      after: this.cloneState(request.after),
      changes: this.normalizeChanges(request.changes),
      createdAt: request.createdAt ?? Date.now(),
      metadata: deepFreeze(cloneValue(request.metadata ?? {})),
    });
  }

  static replace<TState>(
    entry: TimelineHistoryEntry<TState>,
    patch: Partial<Pick<TimelineHistoryEntry<TState>, "after" | "changes" | "createdAt" | "metadata">>,
  ): TimelineHistoryEntry<TState> {
    return deepFreeze({
      ...entry,
      after: patch.after ? this.cloneState(patch.after) : entry.after,
      changes: patch.changes ? this.normalizeChanges(patch.changes) : entry.changes,
      createdAt: patch.createdAt ?? entry.createdAt,
      metadata: patch.metadata ? deepFreeze(cloneValue(patch.metadata)) : entry.metadata,
    });
  }
}
