import type { ProfessionalSnapCandidate, ProfessionalSnapMatch, ProfessionalSnapRequest, ProfessionalSnapSource, ProfessionalSnapStrength } from "../contracts/professional-snapping-contracts";

export class ProfessionalSnapDistanceRuntime {
  constructor(
    private readonly defaultThresholdPixels = 10,
    private readonly defaultThresholdSeconds = 0.08,
    private readonly preferSameTrack = true,
    private readonly priorities: Partial<Record<ProfessionalSnapSource, number>> = {},
  ) {}

  evaluate(candidate: ProfessionalSnapCandidate, request: ProfessionalSnapRequest): ProfessionalSnapMatch | null {
    const deltaSeconds = candidate.time - request.proposedTime;
    const absoluteSeconds = Math.abs(deltaSeconds);
    const pixelsPerSecond = request.pixelsPerSecond && request.pixelsPerSecond > 0 ? request.pixelsPerSecond : null;
    const distancePixels = pixelsPerSecond === null ? null : absoluteSeconds * pixelsPerSecond;
    const thresholdSeconds = request.thresholdSeconds ?? (pixelsPerSecond === null ? this.defaultThresholdSeconds : Number.POSITIVE_INFINITY);
    const thresholdPixels = request.thresholdPixels ?? this.defaultThresholdPixels;
    if (absoluteSeconds > thresholdSeconds) return null;
    if (distancePixels !== null && distancePixels > thresholdPixels) return null;

    const sourcePriority = this.priorities[candidate.source] ?? 0;
    const candidatePriority = candidate.priority ?? 0;
    const sameTrackBonus = this.preferSameTrack && request.activeTrackId && candidate.trackId === request.activeTrackId ? 100 : 0;
    const distancePenalty = distancePixels ?? absoluteSeconds * 1000;
    const score = sourcePriority * 1000 + candidatePriority * 100 + sameTrackBonus - distancePenalty;
    const ratio = distancePixels !== null ? distancePixels / Math.max(1, thresholdPixels) : absoluteSeconds / Math.max(0.000001, thresholdSeconds);
    const strength: ProfessionalSnapStrength = ratio <= 0.25 ? "strong" : ratio <= 0.65 ? "normal" : "soft";
    return Object.freeze({ candidate, proposedTime: request.proposedTime, snappedTime: candidate.time, deltaSeconds, distancePixels, score, strength });
  }

  chooseBest(candidates: readonly ProfessionalSnapCandidate[], request: ProfessionalSnapRequest): ProfessionalSnapMatch | null {
    const matches = candidates.map(candidate => this.evaluate(candidate, request)).filter((match): match is ProfessionalSnapMatch => match !== null);
    matches.sort((a, b) => b.score - a.score || Math.abs(a.deltaSeconds) - Math.abs(b.deltaSeconds) || a.candidate.candidateId.localeCompare(b.candidate.candidateId));
    return matches[0] ?? null;
  }
}
