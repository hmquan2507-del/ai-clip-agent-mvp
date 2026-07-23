import type { ProfessionalSnapGuide, ProfessionalSnapMatch } from "../contracts/professional-snapping-contracts";

const LABELS: Record<string, string> = {
  "clip-start": "Clip start", "clip-end": "Clip end", playhead: "Playhead", marker: "Marker",
  keyframe: "Keyframe", "transition-start": "Transition start", "transition-end": "Transition end",
  "audio-peak": "Audio peak", "subtitle-cue": "Subtitle cue", "timeline-start": "Timeline start",
  "timeline-end": "Timeline end", custom: "Snap point",
};

export class ProfessionalSnappingGuideRuntime {
  create(match: ProfessionalSnapMatch): ProfessionalSnapGuide {
    const candidate = match.candidate;
    return Object.freeze({
      guideId: `snap-guide:${candidate.candidateId}`,
      time: match.snappedTime,
      source: candidate.source,
      label: LABELS[candidate.source] ?? "Snap point",
      deltaSeconds: match.deltaSeconds,
      distancePixels: match.distancePixels,
      trackId: candidate.trackId ?? null,
      entityId: candidate.entityId ?? null,
      visible: true,
    });
  }

  createMany(match: ProfessionalSnapMatch | null): readonly ProfessionalSnapGuide[] {
    return match ? Object.freeze([this.create(match)]) : Object.freeze([]);
  }
}
