import type { ProfessionalMagneticPreview, ProfessionalSnapGuide, ProfessionalSnapMatch } from "../contracts/professional-snapping-contracts";

export class ProfessionalMagneticTimelineRuntime {
  createPreview(originalTime: number, match: ProfessionalSnapMatch | null, guides: readonly ProfessionalSnapGuide[]): ProfessionalMagneticPreview {
    const previewTime = match?.snappedTime ?? originalTime;
    return Object.freeze({
      active: match !== null,
      originalTime,
      previewTime,
      displacementSeconds: previewTime - originalTime,
      match,
      guides: Object.freeze([...guides]),
    });
  }
}
