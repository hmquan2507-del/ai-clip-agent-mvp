import type { TimelineKeyframeDragPreview, TimelineKeyframeMutationPort, TimelineKeyframeSnapCandidate } from "../contracts/timeline-keyframe-overlay-contracts";
import { TimelineKeyframeSnapRuntime } from "./timeline-keyframe-snap-runtime";

export class TimelineKeyframeDragRuntime {
  private preview: TimelineKeyframeDragPreview | null = null;
  constructor(private readonly keyframes: TimelineKeyframeMutationPort, private readonly snap = new TimelineKeyframeSnapRuntime()) {}
  getPreview(): TimelineKeyframeDragPreview | null { return this.preview; }
  begin(keyframeIds: readonly string[]): void {
    const unique = [...new Set(keyframeIds)];
    if (!unique.length) throw new Error("At least one keyframe is required for drag.");
    this.preview = Object.freeze({ keyframeIds: Object.freeze(unique), deltaSeconds: 0, targetTimes: Object.freeze({}), snap: Object.freeze({ snapped: false, kind: "none", requestedTimeSeconds: 0, resolvedTimeSeconds: 0, distanceSeconds: 0, sourceId: null }) });
  }
  update(deltaSeconds: number, candidates: readonly TimelineKeyframeSnapCandidate[], thresholdSeconds: number): TimelineKeyframeDragPreview {
    if (!this.preview) throw new Error("Keyframe drag has not started.");
    const source = this.keyframes.getKeyframes().filter((item) => this.preview!.keyframeIds.includes(item.keyframeId));
    const anchor = source.slice().sort((a, b) => a.timeSeconds - b.timeSeconds)[0];
    if (!anchor) throw new Error("Dragged keyframes are no longer available.");
    const requestedAnchor = Math.max(0, anchor.timeSeconds + deltaSeconds);
    const snap = this.snap.resolve(requestedAnchor, candidates, thresholdSeconds);
    const resolvedDelta = snap.resolvedTimeSeconds - anchor.timeSeconds;
    const targetTimes: Record<string, number> = {};
    source.forEach((item) => { targetTimes[item.keyframeId] = Math.max(0, item.timeSeconds + resolvedDelta); });
    this.preview = Object.freeze({ keyframeIds: this.preview.keyframeIds, deltaSeconds: resolvedDelta, targetTimes: Object.freeze(targetTimes), snap });
    return this.preview;
  }
  commit(): readonly string[] {
    if (!this.preview) return Object.freeze([]);
    const ids = this.preview.keyframeIds;
    for (const id of ids) this.keyframes.moveKeyframe(id, this.preview.targetTimes[id]);
    this.preview = null;
    return ids;
  }
  cancel(): void { this.preview = null; }
}
