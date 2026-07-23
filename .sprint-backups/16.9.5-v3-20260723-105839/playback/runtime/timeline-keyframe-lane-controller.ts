import type { TimelineInterpolation, TimelineKeyframe } from "../contracts/timeline-effects-animation-contracts";
import type { TimelineKeyframeLaneGeometry, TimelineKeyframeOverlayState, TimelineKeyframeSnapCandidate, TimelineKeyframeMutationPort } from "../contracts/timeline-keyframe-overlay-contracts";
import { TimelineKeyframeDragRuntime } from "./timeline-keyframe-drag-runtime";
import { TimelineKeyframeOverlayRuntime } from "./timeline-keyframe-overlay-runtime";

export type TimelineKeyframeLaneListener = (state: TimelineKeyframeOverlayState) => void;

export class TimelineKeyframeLaneController {
  readonly overlay = new TimelineKeyframeOverlayRuntime();
  readonly drag: TimelineKeyframeDragRuntime;
  private readonly listeners = new Set<TimelineKeyframeLaneListener>();
  private geometry: TimelineKeyframeLaneGeometry | null = null;
  constructor(private readonly keyframes: TimelineKeyframeMutationPort, private readonly idFactory: () => string = () => `key-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`) { this.drag = new TimelineKeyframeDragRuntime(keyframes); }
  subscribe(listener: TimelineKeyframeLaneListener): () => void { this.listeners.add(listener); listener(this.getState()); return () => this.listeners.delete(listener); }
  setGeometry(geometry: TimelineKeyframeLaneGeometry | null): void { this.geometry = geometry; this.emit(); }
  getState(): TimelineKeyframeOverlayState { return this.overlay.buildState(this.geometry, this.keyframes.getKeyframes(this.geometry?.clipId), this.drag.getPreview()); }
  select(keyframeId: string, options: { toggle?: boolean; range?: boolean } = {}): void {
    const ordered = this.keyframes.getKeyframes(this.geometry?.clipId).map((item) => item.keyframeId);
    if (options.range) this.overlay.selection.selectRange(ordered, keyframeId); else if (options.toggle) this.overlay.selection.toggle(keyframeId); else this.overlay.selection.selectOnly(keyframeId);
    this.overlay.notifySelectionChanged(); this.emit();
  }
  clearSelection(): void { this.overlay.selection.clear(); this.overlay.notifySelectionChanged(); this.emit(); }
  beginDrag(keyframeId: string): void { if (!this.overlay.selection.isSelected(keyframeId)) this.select(keyframeId); this.drag.begin(this.overlay.selection.getSelectedIds()); this.emit(); }
  updateDrag(deltaPixels: number, candidates: readonly TimelineKeyframeSnapCandidate[], thresholdPixels = 8): void {
    if (!this.geometry) return;
    this.drag.update(deltaPixels / this.geometry.pixelsPerSecond, candidates, thresholdPixels / this.geometry.pixelsPerSecond); this.emit();
  }
  commitDrag(): readonly string[] { const ids = this.drag.commit(); this.emit(); return ids; }
  cancelDrag(): void { this.drag.cancel(); this.emit(); }
  deleteSelected(): readonly string[] { const ids = this.overlay.selection.getSelectedIds(); ids.forEach((id) => this.keyframes.removeKeyframe(id)); this.clearSelection(); return ids; }
  duplicateSelected(offsetSeconds = 0.1): readonly TimelineKeyframe[] {
    const selected = this.keyframes.getKeyframes().filter((item) => this.overlay.selection.isSelected(item.keyframeId));
    const copies = selected.map((item) => this.keyframes.addKeyframe(Object.freeze({ ...item, keyframeId: this.idFactory(), timeSeconds: Math.max(0, item.timeSeconds + offsetSeconds) })));
    this.overlay.selection.clear(); this.overlay.selection.add(copies.map((item) => item.keyframeId)); this.overlay.notifySelectionChanged(); this.emit(); return Object.freeze(copies);
  }
  setInterpolation(interpolation: TimelineInterpolation): void {
    const selected = this.keyframes.getKeyframes().filter((item) => this.overlay.selection.isSelected(item.keyframeId));
    for (const item of selected) {
      this.keyframes.removeKeyframe(item.keyframeId);
      this.keyframes.addKeyframe(Object.freeze({ ...item, interpolation }));
    }
    this.emit();
  }
  private emit(): void { const state = this.getState(); this.listeners.forEach((listener) => listener(state)); }
}
