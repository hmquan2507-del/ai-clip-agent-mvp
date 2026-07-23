import { TIMELINE_EFFECTS_ANIMATION_CONTRACT_VERSION, type TimelineAnimatableProperty, type TimelineEvaluatedProperty, type TimelineKeyframe } from "../contracts/timeline-effects-animation-contracts";
import { TimelineKeyframeModel } from "./timeline-keyframe-model";

export class TimelineAnimationTrackRuntime {
  private readonly keyframes = new Map<string, TimelineKeyframe>();
  private version = 0;

  addKeyframe(keyframe: TimelineKeyframe): TimelineKeyframe {
    if (this.keyframes.has(keyframe.keyframeId)) throw new Error(`Keyframe already exists: ${keyframe.keyframeId}`);
    return this.upsertKeyframe(keyframe);
  }

  upsertKeyframe(keyframe: TimelineKeyframe): TimelineKeyframe {
    if (!keyframe.clipId.trim()) throw new Error("Keyframe clipId is required.");
    if (!Number.isFinite(keyframe.timeSeconds) || keyframe.timeSeconds < 0) throw new Error("Keyframe time must be finite and non-negative.");
    if (!Number.isFinite(keyframe.value)) throw new Error("Keyframe value must be finite.");
    const normalized = Object.freeze({ ...keyframe });
    this.keyframes.set(normalized.keyframeId, normalized);
    this.version += 1;
    return normalized;
  }

  removeKeyframe(keyframeId: string): boolean {
    const removed = this.keyframes.delete(keyframeId);
    if (removed) this.version += 1;
    return removed;
  }

  moveKeyframe(keyframeId: string, timeSeconds: number, value?: number): TimelineKeyframe {
    const current = this.keyframes.get(keyframeId);
    if (!current) throw new Error(`Unknown keyframe: ${keyframeId}`);
    return this.upsertKeyframe({ ...current, timeSeconds, value: value ?? current.value });
  }

  getKeyframes(clipId?: string, property?: TimelineAnimatableProperty): readonly TimelineKeyframe[] {
    return TimelineKeyframeModel.normalize([...this.keyframes.values()].filter((item) =>
      (!clipId || item.clipId === clipId) && (!property || item.property === property)));
  }

  evaluate(clipId: string, property: TimelineAnimatableProperty, timeSeconds: number): TimelineEvaluatedProperty | null {
    return TimelineKeyframeModel.evaluate(this.getKeyframes(clipId, property), timeSeconds);
  }

  evaluateClip(clipId: string, timeSeconds: number): readonly TimelineEvaluatedProperty[] {
    const properties = new Set(this.getKeyframes(clipId).map((item) => item.property));
    return Object.freeze([...properties].map((property) => this.evaluate(clipId, property, timeSeconds)).filter((item): item is TimelineEvaluatedProperty => Boolean(item)));
  }

  clearClip(clipId: string): number {
    let removed = 0;
    for (const item of [...this.keyframes.values()]) if (item.clipId === clipId && this.keyframes.delete(item.keyframeId)) removed += 1;
    if (removed) this.version += 1;
    return removed;
  }

  getSnapshot() {
    return Object.freeze({ contractVersion: TIMELINE_EFFECTS_ANIMATION_CONTRACT_VERSION, version: this.version, keyframes: this.getKeyframes() });
  }

  restore(keyframes: readonly TimelineKeyframe[]): void {
    this.keyframes.clear();
    for (const keyframe of keyframes) this.upsertKeyframe(keyframe);
    this.version += 1;
  }
}
