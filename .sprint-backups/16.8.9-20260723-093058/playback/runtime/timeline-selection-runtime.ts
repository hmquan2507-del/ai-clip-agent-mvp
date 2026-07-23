import {
  TIMELINE_SELECTION_CONTRACT_VERSION,
  type TimelineSelectionConfiguration,
  type TimelineSelectionEventType,
  type TimelineSelectionListener,
  type TimelineSelectionSnapshot,
} from "../contracts/timeline-selection-contracts";
import { SelectionHistoryModel, type SelectionHistoryEntry } from "./selection-history-model";

const unique = (ids: readonly string[]): string[] => [...new Set(ids.filter(Boolean))];

export class TimelineSelectionRuntime {
  private status: TimelineSelectionSnapshot["status"] = "idle";
  private version = 0;
  private orderedClipIds: string[];
  private selectedClipIds: string[] = [];
  private activeClipId: string | null = null;
  private focusedClipId: string | null = null;
  private anchorClipId: string | null = null;
  private lastSelectedClipId: string | null = null;
  private readonly listeners = new Set<TimelineSelectionListener>();
  private readonly history: SelectionHistoryModel;

  constructor(configuration: TimelineSelectionConfiguration = {}) {
    this.orderedClipIds = unique(configuration.orderedClipIds ?? []);
    this.history = new SelectionHistoryModel(configuration.historyLimit ?? 50);
  }

  configure(configuration: TimelineSelectionConfiguration): TimelineSelectionSnapshot {
    this.assertUsable();
    if (configuration.orderedClipIds) this.orderedClipIds = unique(configuration.orderedClipIds);
    if (this.status === "idle") this.status = "ready";
    return this.emit("selection_changed");
  }

  ready(): TimelineSelectionSnapshot {
    this.assertUsable();
    if (this.status !== "ready") { this.status = "ready"; return this.emit("selection_changed"); }
    return this.getSnapshot();
  }

  selectOnly(clipId: string): TimelineSelectionSnapshot {
    this.assertUsable();
    if (!clipId) return this.getSnapshot();
    this.capture();
    this.status = "selecting";
    this.selectedClipIds = [clipId];
    this.activeClipId = clipId;
    this.focusedClipId = clipId;
    this.anchorClipId = clipId;
    this.lastSelectedClipId = clipId;
    this.status = "ready";
    return this.emit("selection_changed");
  }

  select(clipId: string): TimelineSelectionSnapshot {
    this.assertUsable();
    if (!clipId || this.selectedClipIds.includes(clipId)) return this.getSnapshot();
    this.capture();
    this.selectedClipIds = [...this.selectedClipIds, clipId];
    this.activeClipId = clipId;
    this.focusedClipId = clipId;
    this.anchorClipId ??= clipId;
    this.lastSelectedClipId = clipId;
    return this.emit("selection_changed");
  }

  toggle(clipId: string): TimelineSelectionSnapshot {
    this.assertUsable();
    if (!clipId) return this.getSnapshot();
    this.capture();
    if (this.selectedClipIds.includes(clipId)) {
      this.selectedClipIds = this.selectedClipIds.filter(id => id !== clipId);
      if (this.activeClipId === clipId) this.activeClipId = this.selectedClipIds.at(-1) ?? null;
      if (this.focusedClipId === clipId) this.focusedClipId = this.activeClipId;
      if (this.anchorClipId === clipId) this.anchorClipId = this.selectedClipIds[0] ?? null;
    } else {
      this.selectedClipIds = [...this.selectedClipIds, clipId];
      this.activeClipId = clipId;
      this.focusedClipId = clipId;
      this.anchorClipId ??= clipId;
      this.lastSelectedClipId = clipId;
    }
    return this.emit("selection_changed");
  }

  selectRange(targetClipId: string, orderedClipIds: readonly string[] = this.orderedClipIds): TimelineSelectionSnapshot {
    this.assertUsable();
    const order = unique(orderedClipIds);
    const anchor = this.anchorClipId ?? this.activeClipId ?? targetClipId;
    const a = order.indexOf(anchor), b = order.indexOf(targetClipId);
    if (a < 0 || b < 0) return this.selectOnly(targetClipId);
    this.capture();
    const [start, end] = a <= b ? [a, b] : [b, a];
    this.selectedClipIds = order.slice(start, end + 1);
    this.activeClipId = targetClipId;
    this.focusedClipId = targetClipId;
    this.anchorClipId = anchor;
    this.lastSelectedClipId = targetClipId;
    return this.emit("selection_changed");
  }

  clear(): TimelineSelectionSnapshot {
    this.assertUsable();
    if (!this.selectedClipIds.length && !this.activeClipId && !this.focusedClipId) return this.getSnapshot();
    this.capture();
    this.selectedClipIds = [];
    this.activeClipId = this.focusedClipId = this.anchorClipId = this.lastSelectedClipId = null;
    return this.emit("selection_changed");
  }

  setActive(clipId: string | null): TimelineSelectionSnapshot {
    this.assertUsable();
    if (clipId === this.activeClipId) return this.getSnapshot();
    this.capture();
    this.activeClipId = clipId;
    if (clipId && !this.selectedClipIds.includes(clipId)) this.selectedClipIds = [...this.selectedClipIds, clipId];
    return this.emit("active_changed");
  }

  setFocused(clipId: string | null): TimelineSelectionSnapshot {
    this.assertUsable();
    if (clipId === this.focusedClipId) return this.getSnapshot();
    this.focusedClipId = clipId;
    return this.emit("focus_changed");
  }

  moveFocusNext(orderedClipIds: readonly string[] = this.orderedClipIds): TimelineSelectionSnapshot {
    return this.moveFocus(1, orderedClipIds);
  }

  moveFocusPrevious(orderedClipIds: readonly string[] = this.orderedClipIds): TimelineSelectionSnapshot {
    return this.moveFocus(-1, orderedClipIds);
  }

  restorePreviousSelection(): TimelineSelectionSnapshot {
    this.assertUsable();
    const entry = this.history.restore();
    if (!entry) return this.getSnapshot();
    this.applyEntry(entry);
    return this.emit("history_restored");
  }

  subscribe(listener: TimelineSelectionListener): () => void {
    this.assertUsable();
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  reset(): TimelineSelectionSnapshot {
    this.assertUsable();
    this.history.clear();
    this.selectedClipIds = [];
    this.activeClipId = this.focusedClipId = this.anchorClipId = this.lastSelectedClipId = null;
    this.status = "idle";
    return this.emit("reset");
  }

  dispose(): void {
    if (this.status === "disposed") return;
    this.status = "disposed";
    const snapshot = this.emit("disposed");
    this.listeners.clear();
    void snapshot;
  }

  getSnapshot(): TimelineSelectionSnapshot {
    return Object.freeze({
      contractVersion: TIMELINE_SELECTION_CONTRACT_VERSION,
      version: this.version,
      status: this.status,
      selectedClipIds: Object.freeze([...this.selectedClipIds]),
      activeClipId: this.activeClipId,
      focusedClipId: this.focusedClipId,
      anchorClipId: this.anchorClipId,
      lastSelectedClipId: this.lastSelectedClipId,
      selectionCount: this.selectedClipIds.length,
      historyDepth: this.history.size,
    });
  }

  private moveFocus(delta: number, orderedClipIds: readonly string[]): TimelineSelectionSnapshot {
    this.assertUsable();
    const order = unique(orderedClipIds);
    if (!order.length) return this.getSnapshot();
    const current = this.focusedClipId ?? this.activeClipId;
    const currentIndex = current ? order.indexOf(current) : -1;
    const nextIndex = Math.min(order.length - 1, Math.max(0, currentIndex < 0 ? 0 : currentIndex + delta));
    return this.setFocused(order[nextIndex]);
  }

  private capture(): void { this.history.capture(this.getSnapshot()); }
  private applyEntry(entry: SelectionHistoryEntry): void {
    this.selectedClipIds = [...entry.selectedClipIds];
    this.activeClipId = entry.activeClipId;
    this.focusedClipId = entry.focusedClipId;
    this.anchorClipId = entry.anchorClipId;
    this.lastSelectedClipId = entry.lastSelectedClipId;
  }
  private emit(type: TimelineSelectionEventType): TimelineSelectionSnapshot {
    this.version += 1;
    const snapshot = this.getSnapshot();
    for (const listener of this.listeners) listener({ type, snapshot });
    return snapshot;
  }
  private assertUsable(): void {
    if (this.status === "disposed") throw new Error("TimelineSelectionRuntime is disposed");
  }
}

export const createTimelineSelectionRuntime = (configuration: TimelineSelectionConfiguration = {}): TimelineSelectionRuntime =>
  new TimelineSelectionRuntime(configuration);
