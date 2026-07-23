import type {
  CreateTimelineHistoryCheckpointRequest,
  RemoveTimelineHistoryCheckpointRequest,
  TimelineHistoryCheckpoint,
  TimelineHistoryCheckpointResult,
  TimelineHistoryConflict,
  TimelineHistoryJsonValue,
  TimelineUndoRedoHistorySnapshot,
} from "../contracts/timeline-history-contracts";
import { TimelineHistoryCheckpointModel } from "./timeline-history-checkpoint-model";

export interface TimelineHistoryCheckpointManagerConfiguration {
  readonly maxCheckpoints?: number;
  readonly autoCheckpointInterval?: number;
  readonly autoCheckpointPrefix?: string;
}

export interface TimelineHistoryCheckpointRemovalResult<TState = TimelineHistoryJsonValue> {
  readonly removed: boolean;
  readonly checkpoint: TimelineHistoryCheckpoint<TState> | null;
  readonly checkpoints: readonly TimelineHistoryCheckpoint<TState>[];
  readonly conflicts: readonly TimelineHistoryConflict[];
}

const makeConflict = (code: TimelineHistoryConflict["code"], message: string, checkpointId?: string): TimelineHistoryConflict =>
  Object.freeze({ code, message, blocking: true, checkpointId: checkpointId ?? null });

export class TimelineHistoryCheckpointManager<TState = TimelineHistoryJsonValue> {
  private readonly maxCheckpoints: number;
  private readonly autoCheckpointInterval: number;
  private readonly autoCheckpointPrefix: string;
  private checkpoints: readonly TimelineHistoryCheckpoint<TState>[] = Object.freeze([]);
  private sequence = 0;

  constructor(configuration: TimelineHistoryCheckpointManagerConfiguration = {}) {
    this.maxCheckpoints = configuration.maxCheckpoints ?? 20;
    this.autoCheckpointInterval = configuration.autoCheckpointInterval ?? 25;
    this.autoCheckpointPrefix = configuration.autoCheckpointPrefix ?? "auto";
    if (!Number.isInteger(this.maxCheckpoints) || this.maxCheckpoints < 0) throw new Error("Maximum checkpoints must be a non-negative integer.");
    if (!Number.isInteger(this.autoCheckpointInterval) || this.autoCheckpointInterval < 1) throw new Error("Auto checkpoint interval must be a positive integer.");
  }

  synchronize(snapshot: TimelineUndoRedoHistorySnapshot<TState>): readonly TimelineHistoryCheckpoint<TState>[] {
    this.checkpoints = TimelineHistoryCheckpointModel.sort(snapshot.checkpoints);
    return this.getCheckpoints();
  }

  create(request: CreateTimelineHistoryCheckpointRequest<TState>, branchId: string): TimelineHistoryCheckpointResult<TState> {
    if (this.checkpoints.some((checkpoint) => checkpoint.checkpointId === request.checkpointId)) {
      const conflicts = Object.freeze([makeConflict("duplicate-checkpoint-id", "Timeline history checkpoint id already exists.", request.checkpointId)]);
      return Object.freeze({ created: false, checkpoint: null, evictedCheckpointIds: Object.freeze([]), conflicts });
    }
    const checkpoint = TimelineHistoryCheckpointModel.create(request, branchId);
    const capacity = TimelineHistoryCheckpointModel.enforceCapacity([...this.checkpoints, checkpoint], this.maxCheckpoints);
    this.checkpoints = capacity.checkpoints;
    return Object.freeze({ created: true, checkpoint, evictedCheckpointIds: capacity.evictedCheckpointIds, conflicts: Object.freeze([]) });
  }

  createFromSnapshot(snapshot: TimelineUndoRedoHistorySnapshot<TState>, request: Omit<CreateTimelineHistoryCheckpointRequest<TState>, "state" | "entryId"> & { readonly entryId?: string | null }): TimelineHistoryCheckpointResult<TState> {
    if (!snapshot.current) {
      const conflicts = Object.freeze([makeConflict("invalid-state-payload", "Timeline history snapshot does not contain a current state.", request.checkpointId)]);
      return Object.freeze({ created: false, checkpoint: null, evictedCheckpointIds: Object.freeze([]), conflicts });
    }
    return this.create({ ...request, state: snapshot.current, entryId: request.entryId ?? snapshot.past.at(-1)?.entryId ?? null }, snapshot.activeBranchId);
  }

  maybeCreateAutomatic(snapshot: TimelineUndoRedoHistorySnapshot<TState>, label = "Automatic checkpoint"): TimelineHistoryCheckpointResult<TState> | null {
    if (snapshot.past.length === 0 || snapshot.past.length % this.autoCheckpointInterval !== 0) return null;
    this.sequence += 1;
    return this.createFromSnapshot(snapshot, {
      checkpointId: `${this.autoCheckpointPrefix}-${snapshot.activeBranchId}-${snapshot.past.length}-${this.sequence}`,
      label,
      protected: false,
      createdAt: Date.now(),
      metadata: Object.freeze({ automatic: true, historyVersion: snapshot.version }),
    });
  }

  remove(request: RemoveTimelineHistoryCheckpointRequest): TimelineHistoryCheckpointRemovalResult<TState> {
    const checkpoint = this.checkpoints.find((item) => item.checkpointId === request.checkpointId) ?? null;
    if (!checkpoint) {
      const conflicts = Object.freeze([makeConflict("checkpoint-not-found", "Timeline history checkpoint was not found.", request.checkpointId)]);
      return Object.freeze({ removed: false, checkpoint: null, checkpoints: this.getCheckpoints(), conflicts });
    }
    if (checkpoint.protected && !request.force) {
      const conflicts = Object.freeze([makeConflict("checkpoint-protected", "Protected timeline history checkpoint cannot be removed without force.", request.checkpointId)]);
      return Object.freeze({ removed: false, checkpoint, checkpoints: this.getCheckpoints(), conflicts });
    }
    this.checkpoints = Object.freeze(this.checkpoints.filter((item) => item.checkpointId !== request.checkpointId));
    return Object.freeze({ removed: true, checkpoint, checkpoints: this.getCheckpoints(), conflicts: Object.freeze([]) });
  }

  get(checkpointId: string): TimelineHistoryCheckpoint<TState> | null {
    return this.checkpoints.find((checkpoint) => checkpoint.checkpointId === checkpointId) ?? null;
  }

  getLatest(branchId?: string): TimelineHistoryCheckpoint<TState> | null {
    return [...this.checkpoints].reverse().find((checkpoint) => branchId == null || checkpoint.branchId === branchId) ?? null;
  }

  getCheckpoints(): readonly TimelineHistoryCheckpoint<TState>[] {
    return Object.freeze([...this.checkpoints]);
  }

  clear(includeProtected = false): readonly TimelineHistoryCheckpoint<TState>[] {
    this.checkpoints = includeProtected ? Object.freeze([]) : Object.freeze(this.checkpoints.filter((checkpoint) => checkpoint.protected));
    return this.getCheckpoints();
  }
}
