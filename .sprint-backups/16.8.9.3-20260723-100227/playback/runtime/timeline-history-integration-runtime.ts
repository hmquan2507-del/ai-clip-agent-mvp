import {
  TIMELINE_HISTORY_INTEGRATION_CONTRACT_VERSION,
  type TimelineHistoryCommand,
  type TimelineHistoryCommandResult,
  type TimelineHistoryIntegrationConfiguration,
  type TimelineHistoryIntegrationEvent,
  type TimelineHistoryIntegrationListener,
  type TimelineHistoryIntegrationSnapshot,
  type TimelineHistoryRestoreContext,
  type TimelineHistoryStateAdapter,
  type TimelineHistoryUndoRedoResult,
} from "../contracts/timeline-history-integration-contracts";
import type {
  TimelineHistoryConflict,
  TimelineHistoryJsonValue,
  TimelineHistoryStatePayload,
} from "../contracts/timeline-history-contracts";
import { TimelineHistorySnapshotPersistence } from "./timeline-history-snapshot-persistence";
import { TimelineUndoRedoHistoryRuntime } from "./timeline-undo-redo-history-runtime";

const conflict = (message: string): TimelineHistoryConflict => Object.freeze({
  code: "restore-failed",
  message,
  blocking: true,
});

export class TimelineHistoryIntegrationRuntime<TState = TimelineHistoryJsonValue> {
  private readonly history: TimelineUndoRedoHistoryRuntime<TState>;
  private readonly listeners = new Set<TimelineHistoryIntegrationListener<TState>>();
  private readonly restoreOnCommandFailure: boolean;
  private readonly rejectUnchangedState: boolean;
  private readonly persistAfterMutation: boolean;
  private readonly persistenceKey: string;
  private initialized = false;
  private status: TimelineHistoryIntegrationSnapshot<TState>["status"] = "idle";
  private version = 0;
  private lastCommandId: string | null = null;
  private lastError: string | null = null;

  constructor(
    private readonly adapter: TimelineHistoryStateAdapter<TState>,
    configuration: TimelineHistoryIntegrationConfiguration = {},
    private readonly persistence?: TimelineHistorySnapshotPersistence<TState>,
    history?: TimelineUndoRedoHistoryRuntime<TState>,
  ) {
    this.history = history ?? new TimelineUndoRedoHistoryRuntime<TState>();
    this.history.configure(configuration.history ?? {});
    this.restoreOnCommandFailure = configuration.restoreOnCommandFailure ?? true;
    this.rejectUnchangedState = configuration.rejectUnchangedState ?? true;
    this.persistAfterMutation = configuration.persistAfterMutation ?? Boolean(persistence);
    this.persistenceKey = configuration.persistenceKey ?? "timeline-history";
  }

  async initialize(state?: TimelineHistoryStatePayload<TState>): Promise<TimelineHistoryIntegrationSnapshot<TState>> {
    this.assertNotDisposed();
    const baseline = state ?? await this.adapter.captureState();
    this.history.replaceBaseline({ state: baseline, clearHistory: true, clearCheckpoints: false });
    this.initialized = true;
    this.status = "idle";
    this.lastError = null;
    this.bump("initialized");
    return this.getSnapshot();
  }

  async executeCommand(command: TimelineHistoryCommand<TState>): Promise<TimelineHistoryCommandResult<TState>> {
    this.assertReady();
    if (this.isBusy()) throw new Error("Timeline history integration runtime is busy.");
    this.status = "executing-command";
    this.lastCommandId = command.commandId;
    let before: TimelineHistoryStatePayload<TState> | null = null;
    try {
      before = await this.adapter.captureState();
      const execution = await command.execute({ before });
      const after = execution.after ?? await this.adapter.captureState();
      if (this.rejectUnchangedState && before.checksum === after.checksum) {
        this.status = "blocked";
        const conflicts = Object.freeze([conflict("Timeline command did not produce a state change.")]);
        this.lastError = conflicts[0].message;
        this.bump("blocked");
        return Object.freeze({ executed: false, commandId: command.commandId, before, after, recordResult: null, conflicts, error: null });
      }
      const recordResult = this.history.record({
        entryId: command.commandId,
        operation: command.operation,
        label: command.label,
        sourceRuntime: command.sourceRuntime,
        mergeKey: command.mergeKey ?? null,
        before,
        after,
        changes: execution.changes,
        metadata: Object.freeze({ ...(command.metadata ?? {}), ...(execution.metadata ?? {}) }),
      });
      if (!recordResult.recorded) {
        this.status = "blocked";
        this.lastError = recordResult.conflicts[0]?.message ?? "Timeline command history recording failed.";
        this.bump("blocked");
        return Object.freeze({ executed: false, commandId: command.commandId, before, after, recordResult, conflicts: recordResult.conflicts, error: null });
      }
      this.status = "idle";
      this.lastError = null;
      await this.persistIfEnabled();
      this.bump("command-executed");
      return Object.freeze({ executed: true, commandId: command.commandId, before, after, recordResult, conflicts: Object.freeze([]), error: null });
    } catch (error) {
      const normalized = error instanceof Error ? error : new Error(String(error));
      this.lastError = normalized.message;
      this.status = "blocked";
      if (before && this.restoreOnCommandFailure) {
        await this.adapter.restoreState(before, { direction: "workspace-restore", entryId: null, source: "runtime" });
      }
      this.bump("blocked");
      return Object.freeze({ executed: false, commandId: command.commandId, before, after: null, recordResult: null, conflicts: Object.freeze([conflict(normalized.message)]), error: normalized });
    }
  }

  async undo(source: TimelineHistoryRestoreContext["source"] = "api"): Promise<TimelineHistoryUndoRedoResult<TState>> {
    return this.restore("undo", source);
  }

  async redo(source: TimelineHistoryRestoreContext["source"] = "api"): Promise<TimelineHistoryUndoRedoResult<TState>> {
    return this.restore("redo", source);
  }

  async restoreWorkspaceSnapshot(snapshot: TimelineHistoryIntegrationSnapshot<TState>["history"]): Promise<TimelineHistoryIntegrationSnapshot<TState>> {
    this.assertNotDisposed();
    if (!snapshot.current) throw new Error("Workspace history snapshot does not contain a current state.");
    this.status = "restoring";
    await this.adapter.restoreState(snapshot.current, { direction: "workspace-restore", entryId: snapshot.past.at(-1)?.entryId ?? null, source: "workspace" });
    this.history.replaceBaseline({ state: snapshot.current, clearHistory: true, clearCheckpoints: false, branchId: snapshot.activeBranchId });
    this.initialized = true;
    this.status = "idle";
    this.lastError = null;
    this.bump("workspace-restored");
    return this.getSnapshot();
  }

  async saveWorkspace(): Promise<void> {
    this.assertReady();
    if (!this.persistence) return;
    this.status = "persisting";
    await this.persistence.save(this.persistenceKey, this.history.getSnapshot());
    this.status = "idle";
    this.bump("persistence-completed");
  }

  async loadWorkspace(): Promise<boolean> {
    this.assertNotDisposed();
    if (!this.persistence) return false;
    const envelope = await this.persistence.load(this.persistenceKey);
    if (!envelope) return false;
    await this.restoreWorkspaceSnapshot(envelope.snapshot);
    return true;
  }

  subscribe(listener: TimelineHistoryIntegrationListener<TState>): () => void {
    this.assertNotDisposed();
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  getHistoryRuntime(): TimelineUndoRedoHistoryRuntime<TState> { return this.history; }

  getSnapshot(): TimelineHistoryIntegrationSnapshot<TState> {
    const history = this.history.getSnapshot();
    return Object.freeze({
      contractVersion: TIMELINE_HISTORY_INTEGRATION_CONTRACT_VERSION,
      version: this.version,
      status: this.status,
      initialized: this.initialized,
      busy: this.isBusy(),
      canUndo: history.canUndo && !this.isBusy(),
      canRedo: history.canRedo && !this.isBusy(),
      undoLabel: history.past.at(-1)?.label ?? null,
      redoLabel: history.future.at(-1)?.label ?? null,
      lastCommandId: this.lastCommandId,
      lastError: this.lastError,
      history,
    });
  }

  dispose(): void {
    if (this.status === "disposed") return;
    this.status = "disposed";
    this.history.dispose();
    this.bump("disposed");
    this.listeners.clear();
  }

  private async restore(direction: "undo" | "redo", source: TimelineHistoryRestoreContext["source"]): Promise<TimelineHistoryUndoRedoResult<TState>> {
    this.assertReady();
    if (this.isBusy()) throw new Error("Timeline history integration runtime is busy.");
    this.status = "restoring";
    const restoreResult = direction === "undo" ? this.history.undo() : this.history.redo();
    if (!restoreResult.restored || !restoreResult.state) {
      this.status = "blocked";
      this.lastError = restoreResult.conflicts[0]?.message ?? `Timeline ${direction} failed.`;
      this.bump("blocked");
      return Object.freeze({ completed: false, restoreResult, error: null });
    }
    try {
      await this.adapter.restoreState(restoreResult.state, { direction, entryId: restoreResult.entry?.entryId ?? null, source });
      this.status = "idle";
      this.lastError = null;
      await this.persistIfEnabled();
      this.bump(direction === "undo" ? "undo-completed" : "redo-completed");
      return Object.freeze({ completed: true, restoreResult, error: null });
    } catch (error) {
      const normalized = error instanceof Error ? error : new Error(String(error));
      this.status = "blocked";
      this.lastError = normalized.message;
      this.bump("blocked");
      return Object.freeze({ completed: false, restoreResult, error: normalized });
    }
  }

  private async persistIfEnabled(): Promise<void> {
    if (this.persistAfterMutation && this.persistence) await this.persistence.save(this.persistenceKey, this.history.getSnapshot());
  }

  private isBusy(): boolean { return this.status === "executing-command" || this.status === "restoring" || this.status === "persisting"; }
  private assertReady(): void { this.assertNotDisposed(); if (!this.initialized) throw new Error("Timeline history integration runtime is not initialized."); }
  private assertNotDisposed(): void { if (this.status === "disposed") throw new Error("Timeline history integration runtime is disposed."); }
  private bump(type: TimelineHistoryIntegrationEvent<TState>["type"]): void {
    this.version += 1;
    const event = Object.freeze({ type, snapshot: this.getSnapshot() });
    for (const listener of [...this.listeners]) listener(event);
  }
}
