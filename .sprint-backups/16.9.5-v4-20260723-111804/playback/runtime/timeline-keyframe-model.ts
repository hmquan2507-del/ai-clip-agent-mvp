import type { TimelineEvaluatedProperty, TimelineInterpolation, TimelineKeyframe } from "../contracts/timeline-effects-animation-contracts";

const clamp01 = (value: number) => Math.max(0, Math.min(1, value));
const easing = (kind: TimelineInterpolation, progress: number): number => {
  const t = clamp01(progress);
  if (kind === "hold") return 0;
  if (kind === "ease-in") return t * t;
  if (kind === "ease-out") return 1 - (1 - t) * (1 - t);
  if (kind === "ease-in-out") return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
  return t;
};

export class TimelineKeyframeModel {
  static normalize(keyframes: readonly TimelineKeyframe[]): readonly TimelineKeyframe[] {
    return Object.freeze([...keyframes]
      .filter((item) => Number.isFinite(item.timeSeconds) && Number.isFinite(item.value))
      .sort((left, right) => left.timeSeconds - right.timeSeconds || left.keyframeId.localeCompare(right.keyframeId)));
  }

  static evaluate(keyframes: readonly TimelineKeyframe[], timeSeconds: number): TimelineEvaluatedProperty | null {
    const ordered = this.normalize(keyframes);
    if (!ordered.length) return null;
    const property = ordered[0].property;
    const exactOrPrevious = [...ordered].reverse().find((item) => item.timeSeconds <= timeSeconds) ?? null;
    const next = ordered.find((item) => item.timeSeconds > timeSeconds) ?? null;
    if (!exactOrPrevious) {
      const first = ordered[0];
      return Object.freeze({ property, value: first.value, previousKeyframeId: null, nextKeyframeId: first.keyframeId, progress: 0 });
    }
    if (!next || exactOrPrevious.timeSeconds === next.timeSeconds) {
      return Object.freeze({ property, value: exactOrPrevious.value, previousKeyframeId: exactOrPrevious.keyframeId, nextKeyframeId: null, progress: 1 });
    }
    const raw = (timeSeconds - exactOrPrevious.timeSeconds) / (next.timeSeconds - exactOrPrevious.timeSeconds);
    const progress = clamp01(raw);
    const eased = easing(exactOrPrevious.interpolation, progress);
    const value = exactOrPrevious.value + (next.value - exactOrPrevious.value) * eased;
    return Object.freeze({ property, value, previousKeyframeId: exactOrPrevious.keyframeId, nextKeyframeId: next.keyframeId, progress });
  }
}
