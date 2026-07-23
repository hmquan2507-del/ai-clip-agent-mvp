import type { ProfessionalSnapCandidate, ProfessionalSnapRequest, ProfessionalSnapSource } from "../contracts/professional-snapping-contracts";

const finite = (value: number, name: string): number => {
  if (!Number.isFinite(value)) throw new Error(`${name} must be finite`);
  return value;
};
const unique = <T>(values: readonly T[]): readonly T[] => Object.freeze([...new Set(values)]);

export class ProfessionalSnapCandidateRuntime {
  static normalize(candidate: ProfessionalSnapCandidate): ProfessionalSnapCandidate {
    if (!candidate.candidateId.trim()) throw new Error("Snap candidate id is required");
    const time = Math.max(0, finite(candidate.time, "Candidate time"));
    return Object.freeze({
      ...candidate,
      candidateId: candidate.candidateId.trim(),
      time,
      trackId: candidate.trackId ?? null,
      entityId: candidate.entityId ?? null,
      priority: Number.isFinite(candidate.priority) ? candidate.priority : 0,
      metadata: Object.freeze({ ...(candidate.metadata ?? {}) }),
    });
  }

  static normalizeMany(candidates: readonly ProfessionalSnapCandidate[]): readonly ProfessionalSnapCandidate[] {
    const map = new Map<string, ProfessionalSnapCandidate>();
    for (const candidate of candidates) map.set(candidate.candidateId, this.normalize(candidate));
    return Object.freeze([...map.values()].sort((a, b) => a.time - b.time || a.candidateId.localeCompare(b.candidateId)));
  }

  static eligible(candidates: readonly ProfessionalSnapCandidate[], request: ProfessionalSnapRequest): readonly ProfessionalSnapCandidate[] {
    const moving = new Set(unique(request.movingEntityIds ?? []));
    const disabled = new Set<ProfessionalSnapSource>(request.disabledSources ?? []);
    return Object.freeze(candidates.filter(candidate => {
      if (disabled.has(candidate.source)) return false;
      if (candidate.entityId && moving.has(candidate.entityId)) return false;
      if (request.includeOtherTracks === false && request.activeTrackId && candidate.trackId && candidate.trackId !== request.activeTrackId) return false;
      return true;
    }));
  }
}
