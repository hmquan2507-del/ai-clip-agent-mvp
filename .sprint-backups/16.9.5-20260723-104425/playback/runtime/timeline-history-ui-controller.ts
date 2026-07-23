import {
  TIMELINE_HISTORY_UI_CONTRACT_VERSION,
  type TimelineHistoryPanelMode,
  type TimelineHistoryToastMessage,
  type TimelineHistoryUiActions,
  type TimelineHistoryUiListener,
  type TimelineHistoryUiState,
} from "../contracts/timeline-history-ui-contracts";
import type { TimelineHistoryCheckpoint, TimelineHistoryEntry, TimelineHistoryJsonValue } from "../contracts/timeline-history-contracts";
import { TimelineHistoryIntegrationRuntime } from "./timeline-history-integration-runtime";

export class TimelineHistoryUiController<TState = TimelineHistoryJsonValue> {
  private readonly listeners = new Set<TimelineHistoryUiListener<TState>>();
  private panelMode: TimelineHistoryPanelMode = "closed";
  private selectedEntryId: string | null = null;
  private selectedCheckpointId: string | null = null;
  private toast: TimelineHistoryToastMessage | null = null;
  private version = 0;
  private disposed = false;
  private readonly unsubscribe: () => void;

  constructor(
    private readonly integration: TimelineHistoryIntegrationRuntime<TState>,
    private readonly actions: TimelineHistoryUiActions<TState> = {},
  ) {
    this.unsubscribe = integration.subscribe((event) => {
      if (event.type === "undo-completed") this.pushToast("undo", "Undo", `${event.snapshot.undoLabel ?? "Action"} reverted`);
      else if (event.type === "redo-completed") this.pushToast("redo", "Redo", `${event.snapshot.redoLabel ?? "Action"} restored`);
      else if (event.type === "blocked" && event.snapshot.lastError) this.pushToast("error", "History action failed", event.snapshot.lastError);
      else this.emit();
    });
  }

  getState(): TimelineHistoryUiState<TState> {
    const integration = this.integration.getSnapshot();
    const entries = Object.freeze([...integration.history.past, ...[...integration.history.future].reverse()]);
    return Object.freeze({
      contractVersion: TIMELINE_HISTORY_UI_CONTRACT_VERSION,
      version: this.version,
      panelMode: this.panelMode,
      selectedEntryId: this.selectedEntryId,
      selectedCheckpointId: this.selectedCheckpointId,
      busy: integration.busy,
      canUndo: integration.canUndo,
      canRedo: integration.canRedo,
      undoLabel: integration.undoLabel,
      redoLabel: integration.redoLabel,
      entries,
      checkpoints: integration.history.checkpoints,
      currentEntryId: integration.history.past.at(-1)?.entryId ?? null,
      toast: this.toast,
      integration,
    });
  }

  subscribe(listener: TimelineHistoryUiListener<TState>): () => void {
    this.assertActive();
    this.listeners.add(listener);
    listener(this.getState());
    return () => this.listeners.delete(listener);
  }

  async undo(): Promise<void> { this.assertActive(); await this.integration.undo("toolbar"); }
  async redo(): Promise<void> { this.assertActive(); await this.integration.redo("toolbar"); }
  togglePanel(mode: Exclude<TimelineHistoryPanelMode, "closed">): void { this.panelMode = this.panelMode === mode ? "closed" : mode; this.emit(); }
  closePanel(): void { this.panelMode = "closed"; this.emit(); }

  async selectEntry(entry: TimelineHistoryEntry<TState>): Promise<void> {
    this.selectedEntryId = entry.entryId;
    this.emit();
    await this.actions.previewEntry?.(entry);
  }

  async createCheckpoint(label: string): Promise<void> {
    const normalized = label.trim();
    if (!normalized) throw new Error("Checkpoint label is required.");
    await this.actions.createCheckpoint?.(normalized);
    this.pushToast("checkpoint", "Checkpoint created", normalized);
  }

  async restoreCheckpoint(checkpoint: TimelineHistoryCheckpoint<TState>): Promise<void> {
    this.selectedCheckpointId = checkpoint.checkpointId;
    this.emit();
    await this.actions.restoreCheckpoint?.(checkpoint);
    this.pushToast("restore", "Checkpoint restored", checkpoint.label);
  }

  async deleteCheckpoint(checkpoint: TimelineHistoryCheckpoint<TState>): Promise<void> {
    await this.actions.deleteCheckpoint?.(checkpoint);
    if (this.selectedCheckpointId === checkpoint.checkpointId) this.selectedCheckpointId = null;
    this.emit();
  }

  dismissToast(): void { this.toast = null; this.emit(); }

  dispose(): void {
    if (this.disposed) return;
    this.disposed = true;
    this.unsubscribe();
    this.listeners.clear();
  }

  private pushToast(kind: TimelineHistoryToastMessage["kind"], title: string, description: string): void {
    this.toast = Object.freeze({ id: `${kind}-${Date.now()}-${this.version + 1}`, kind, title, description, createdAt: Date.now() });
    this.emit();
  }
  private emit(): void { if (this.disposed) return; this.version += 1; const state = this.getState(); for (const listener of [...this.listeners]) listener(state); }
  private assertActive(): void { if (this.disposed) throw new Error("Timeline history UI controller is disposed."); }
}
