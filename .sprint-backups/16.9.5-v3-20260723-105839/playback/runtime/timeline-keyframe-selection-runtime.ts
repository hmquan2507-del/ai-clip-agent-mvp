export class TimelineKeyframeSelectionRuntime {
  private readonly selected = new Set<string>();
  private anchorId: string | null = null;

  getSelectedIds(): readonly string[] { return Object.freeze([...this.selected]); }
  isSelected(keyframeId: string): boolean { return this.selected.has(keyframeId); }
  clear(): void { this.selected.clear(); this.anchorId = null; }
  selectOnly(keyframeId: string): void { this.selected.clear(); this.selected.add(keyframeId); this.anchorId = keyframeId; }
  toggle(keyframeId: string): void { this.selected.has(keyframeId) ? this.selected.delete(keyframeId) : this.selected.add(keyframeId); this.anchorId = keyframeId; }
  add(keyframeIds: readonly string[]): void { keyframeIds.forEach((id) => this.selected.add(id)); if (keyframeIds.length) this.anchorId = keyframeIds[keyframeIds.length - 1]; }
  remove(keyframeId: string): void { this.selected.delete(keyframeId); if (this.anchorId === keyframeId) this.anchorId = null; }
  selectRange(orderedIds: readonly string[], targetId: string): void {
    const anchor = this.anchorId ?? targetId;
    const start = orderedIds.indexOf(anchor);
    const end = orderedIds.indexOf(targetId);
    if (start < 0 || end < 0) { this.selectOnly(targetId); return; }
    this.selected.clear();
    const from = Math.min(start, end); const to = Math.max(start, end);
    for (let index = from; index <= to; index += 1) this.selected.add(orderedIds[index]);
  }
}
