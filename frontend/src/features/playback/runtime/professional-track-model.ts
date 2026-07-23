import type {
  AddProfessionalTrackRequest,
  ProfessionalTrack,
  ProfessionalTrackKind,
  UpdateProfessionalTrackRequest,
} from "../contracts/professional-multi-track-contracts";

const DEFAULT_NAMES: Readonly<Record<ProfessionalTrackKind, string>> = Object.freeze({
  video: "Video", audio: "Audio", subtitle: "Subtitle", overlay: "Overlay",
  effect: "Effect", adjustment: "Adjustment", custom: "Track",
});

export class ProfessionalTrackModel {
  static create(request: AddProfessionalTrackRequest, fallbackOrder: number, defaultColor: string | null): ProfessionalTrack {
    const trackId = request.trackId.trim();
    if (!trackId) throw new Error("trackId is required");
    const name = (request.name?.trim() || DEFAULT_NAMES[request.kind]).trim();
    return Object.freeze({
      trackId,
      name,
      kind: request.kind,
      order: Number.isFinite(request.order) ? Math.max(0, Math.round(request.order!)) : fallbackOrder,
      color: request.color ?? defaultColor,
      locked: false,
      muted: false,
      solo: false,
      hidden: false,
      collapsed: false,
      rippleEnabled: true,
      magneticEnabled: true,
      groupId: request.groupId ?? null,
      status: "active" as const,
      metadata: Object.freeze({ ...(request.metadata ?? {}) }),
    });
  }

  static update(track: ProfessionalTrack, request: UpdateProfessionalTrackRequest): ProfessionalTrack {
    const name = request.name === undefined ? track.name : request.name.trim();
    if (!name) throw new Error("Track name cannot be empty");
    return Object.freeze({
      ...track,
      ...request,
      name,
      metadata: request.metadata === undefined ? track.metadata : Object.freeze({ ...request.metadata }),
    });
  }

  static withOrder(track: ProfessionalTrack, order: number): ProfessionalTrack {
    return Object.freeze({ ...track, order });
  }
}
