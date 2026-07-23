import type { TimelineAnimatableProperty, TimelineKeyframe } from "../contracts/timeline-effects-animation-contracts";

export interface TimelineAnimationOverlaySegment {
  readonly clipId: string;
  readonly property: TimelineAnimatableProperty;
  readonly fromKeyframeId: string;
  readonly toKeyframeId: string;
  readonly startSeconds: number;
  readonly endSeconds: number;
  readonly interpolation: TimelineKeyframe["interpolation"];
}

export class TimelineAnimationOverlayRuntime {
  buildSegments(keyframes: readonly TimelineKeyframe[], clipId: string): readonly TimelineAnimationOverlaySegment[] {
    const grouped = new Map<TimelineAnimatableProperty, TimelineKeyframe[]>();
    keyframes.filter((item) => item.clipId === clipId).forEach((item) => { const bucket = grouped.get(item.property) ?? []; bucket.push(item); grouped.set(item.property, bucket); });
    const segments: TimelineAnimationOverlaySegment[] = [];
    for (const [property, items] of grouped) {
      const ordered = [...items].sort((a, b) => a.timeSeconds - b.timeSeconds);
      for (let index = 0; index < ordered.length - 1; index += 1) {
        const from = ordered[index]; const to = ordered[index + 1];
        segments.push(Object.freeze({ clipId, property, fromKeyframeId: from.keyframeId, toKeyframeId: to.keyframeId, startSeconds: from.timeSeconds, endSeconds: to.timeSeconds, interpolation: from.interpolation }));
      }
    }
    return Object.freeze(segments);
  }
}
