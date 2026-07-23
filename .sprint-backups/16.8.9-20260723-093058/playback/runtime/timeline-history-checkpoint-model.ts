import type {
  CreateTimelineHistoryCheckpointRequest,
  TimelineHistoryCheckpoint,
  TimelineHistoryJsonValue,
} from "../contracts/timeline-history-contracts";
import { TimelineHistoryEntryModel } from "./timeline-history-entry-model";

export interface TimelineHistoryCheckpointCapacityResult<TState = TimelineHistoryJsonValue> {
  readonly checkpoints: readonly TimelineHistoryCheckpoint<TState>[];
  readonly evictedCheckpointIds: readonly string[];
}

export class TimelineHistoryCheckpointModel {
  static create<TState = TimelineHistoryJsonValue>(
    request: CreateTimelineHistoryCheckpointRequest<TState>,
    branchId: string,
  ): TimelineHistoryCheckpoint<TState> {
    if (!request.checkpointId.trim()) throw new Error("Timeline history checkpoint id is required.");
    return Object.freeze({
      checkpointId: request.checkpointId,
      label: request.label,
      entryId: request.entryId ?? null,
      branchId,
      state: TimelineHistoryEntryModel.cloneState(request.state),
      protected: request.protected ?? false,
      createdAt: request.createdAt ?? Date.now(),
      metadata: Object.freeze({ ...(request.metadata ?? {}) }),
    });
  }

  static sort<TState>(checkpoints: readonly TimelineHistoryCheckpoint<TState>[]): readonly TimelineHistoryCheckpoint<TState>[] {
    return Object.freeze(
      [...checkpoints].sort(
        (left, right) => left.createdAt - right.createdAt || left.checkpointId.localeCompare(right.checkpointId),
      ),
    );
  }

  static enforceCapacity<TState>(
    checkpoints: readonly TimelineHistoryCheckpoint<TState>[],
    maxCheckpoints: number,
  ): TimelineHistoryCheckpointCapacityResult<TState> {
    if (!Number.isInteger(maxCheckpoints) || maxCheckpoints < 0) throw new Error("Maximum checkpoints must be a non-negative integer.");
    const ordered = [...this.sort(checkpoints)];
    const evicted: string[] = [];
    while (ordered.length > maxCheckpoints) {
      const index = ordered.findIndex((checkpoint) => !checkpoint.protected);
      if (index < 0) break;
      const [removed] = ordered.splice(index, 1);
      evicted.push(removed.checkpointId);
    }
    return Object.freeze({ checkpoints: Object.freeze(ordered), evictedCheckpointIds: Object.freeze(evicted) });
  }
}
