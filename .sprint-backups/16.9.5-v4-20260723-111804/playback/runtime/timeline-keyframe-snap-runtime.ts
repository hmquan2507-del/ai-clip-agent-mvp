import type { TimelineKeyframeSnapCandidate, TimelineKeyframeSnapResult } from "../contracts/timeline-keyframe-overlay-contracts";

export class TimelineKeyframeSnapRuntime {
  resolve(requestedTimeSeconds: number, candidates: readonly TimelineKeyframeSnapCandidate[], thresholdSeconds: number): TimelineKeyframeSnapResult {
    const safeTime = Math.max(0, requestedTimeSeconds);
    const eligible = candidates
      .map((candidate) => ({ candidate, distance: Math.abs(candidate.timeSeconds - safeTime) }))
      .filter((item) => item.distance <= Math.max(0, thresholdSeconds))
      .sort((left, right) => left.distance - right.distance || right.candidate.priority - left.candidate.priority || left.candidate.timeSeconds - right.candidate.timeSeconds);
    const winner = eligible[0];
    if (!winner) return Object.freeze({ snapped: false, kind: "none", requestedTimeSeconds: safeTime, resolvedTimeSeconds: safeTime, distanceSeconds: 0, sourceId: null });
    return Object.freeze({ snapped: true, kind: winner.candidate.kind, requestedTimeSeconds: safeTime, resolvedTimeSeconds: winner.candidate.timeSeconds, distanceSeconds: winner.distance, sourceId: winner.candidate.sourceId });
  }
}
