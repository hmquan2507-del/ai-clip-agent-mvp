import type {
  RestoreTimelineHistoryCheckpointRequest,
  TimelineHistoryCheckpoint,
  TimelineHistoryConflict,
  TimelineHistoryJsonValue,
  TimelineHistoryRestoreResult,
  TimelineUndoRedoHistorySnapshot,
} from "../contracts/timeline-history-contracts";
import { TimelineHistoryCheckpointManager } from "./timeline-history-checkpoint-manager";
import { TimelineUndoRedoHistoryRuntime } from "./timeline-undo-redo-history-runtime";

const conflict = (code: TimelineHistoryConflict["code"], message: string, checkpointId?: string): TimelineHistoryConflict =>
  Object.freeze({ code, message, blocking: true, checkpointId: checkpointId ?? null });

export class TimelineHistoryRestoreRuntime<TState = TimelineHistoryJsonValue> {
  constructor(
    private readonly history: TimelineUndoRedoHistoryRuntime<TState>,
    private readonly checkpoints: TimelineHistoryCheckpointManager<TState>,
  ) {}

  restoreCheckpoint(request: RestoreTimelineHistoryCheckpointRequest): TimelineHistoryRestoreResult<TState> {
    const checkpoint = this.checkpoints.get(request.checkpointId);
    if (!checkpoint) return this.failure("checkpoint-not-found", "Timeline history checkpoint was not found.", request.checkpointId);
    const current = this.history.getSnapshot().current;
    const conflicts: TimelineHistoryConflict[] = [];
    if (current && request.expectedStateVersion != null && current.stateVersion !== request.expectedStateVersion) conflicts.push(conflict("state-version-conflict", "Expected state version does not match current state.", request.checkpointId));
    if (current && request.expectedTimelineVersion != null && current.timelineVersion !== request.expectedTimelineVersion) conflicts.push(conflict("timeline-version-conflict", "Expected timeline version does not match current state.", request.checkpointId));
    if (current && request.currentChecksum != null && current.checksum !== request.currentChecksum) conflicts.push(conflict("checksum-mismatch", "Current checksum does not match restore request.", request.checkpointId));
    if (conflicts.length > 0) return Object.freeze({ restored: false, direction: "checkpoint", entry: null, checkpoint, state: null, conflicts: Object.freeze(conflicts) });
    this.history.replaceBaseline({ state: checkpoint.state, clearHistory: true, clearCheckpoints: false, branchId: checkpoint.branchId });
    return Object.freeze({ restored: true, direction: "checkpoint", entry: null, checkpoint, state: checkpoint.state, conflicts: Object.freeze([]) });
  }

  restoreLatest(branchId?: string): TimelineHistoryRestoreResult<TState> {
    const checkpoint = this.checkpoints.getLatest(branchId);
    if (!checkpoint) return this.failure("checkpoint-not-found", "No timeline history checkpoint is available.");
    return this.restoreCheckpoint({ checkpointId: checkpoint.checkpointId });
  }

  restoreSnapshot(snapshot: TimelineUndoRedoHistorySnapshot<TState>): TimelineUndoRedoHistorySnapshot<TState> {
    if (!snapshot.current) throw new Error("Timeline history snapshot does not contain a current state.");
    this.checkpoints.synchronize(snapshot);
    return this.history.replaceBaseline({ state: snapshot.current, clearHistory: true, clearCheckpoints: false, branchId: snapshot.activeBranchId });
  }

  private failure(code: TimelineHistoryConflict["code"], message: string, checkpointId?: string): TimelineHistoryRestoreResult<TState> {
    return Object.freeze({ restored: false, direction: "checkpoint", entry: null, checkpoint: null, state: null, conflicts: Object.freeze([conflict(code, message, checkpointId)]) });
  }
}
