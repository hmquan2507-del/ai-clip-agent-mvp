import type { TimelineSelectionSnapshot } from "../contracts/timeline-selection-contracts";

export interface SelectionHistoryEntry {
  readonly selectedClipIds: readonly string[];
  readonly activeClipId: string | null;
  readonly focusedClipId: string | null;
  readonly anchorClipId: string | null;
  readonly lastSelectedClipId: string | null;
}

const cloneEntry = (entry: SelectionHistoryEntry): SelectionHistoryEntry => ({
  selectedClipIds: [...entry.selectedClipIds],
  activeClipId: entry.activeClipId,
  focusedClipId: entry.focusedClipId,
  anchorClipId: entry.anchorClipId,
  lastSelectedClipId: entry.lastSelectedClipId,
});

export class SelectionHistoryModel {
  private readonly entries: SelectionHistoryEntry[] = [];
  constructor(private readonly limit = 50) {}
  capture(snapshot: TimelineSelectionSnapshot): void {
    const next = cloneEntry(snapshot);
    const last = this.entries[this.entries.length - 1];
    if (last && JSON.stringify(last) === JSON.stringify(next)) return;
    this.entries.push(next);
    while (this.entries.length > Math.max(1, this.limit)) this.entries.shift();
  }
  restore(): SelectionHistoryEntry | null {
    const entry = this.entries.pop();
    return entry ? cloneEntry(entry) : null;
  }
  clear(): void { this.entries.length = 0; }
  get size(): number { return this.entries.length; }
}
