import type {
  SlipSlideClipPosition,
  SlipSlideConflict,
  SlipSlideTimelineClip,
  TimelineSlipPreview,
  TimelineSlipSlideConfiguration,
} from "../contracts/slip-slide-edit-contracts";

const freezeConflict = (conflict: SlipSlideConflict): SlipSlideConflict => Object.freeze({ ...conflict });
const freezePosition = (clip: SlipSlideTimelineClip, sourceDelta = 0): SlipSlideClipPosition => Object.freeze({
  clipId: clip.clipId,
  trackId: clip.trackId,
  timelineStartFrame: clip.timelineStartFrame,
  timelineEndFrame: clip.timelineEndFrame,
  sourceStartFrame: clip.sourceStartFrame + sourceDelta,
  sourceEndFrame: clip.sourceEndFrame + sourceDelta,
});

export class SlipPreviewModel {
  static normalizeClip(clip: SlipSlideTimelineClip): SlipSlideTimelineClip {
    return Object.freeze({
      clipId: String(clip.clipId ?? "").trim(),
      trackId: String(clip.trackId ?? "").trim(),
      timelineStartFrame: Math.round(clip.timelineStartFrame),
      timelineEndFrame: Math.round(clip.timelineEndFrame),
      sourceStartFrame: Math.round(clip.sourceStartFrame),
      sourceEndFrame: Math.round(clip.sourceEndFrame),
      sourceDurationFrames: Math.round(clip.sourceDurationFrames),
      locked: Boolean(clip.locked),
    });
  }

  static position(clip: SlipSlideTimelineClip): SlipSlideClipPosition {
    return freezePosition(clip);
  }

  static beginConflicts(clip: SlipSlideTimelineClip, configuration: Required<Omit<TimelineSlipSlideConfiguration, "timelineEndFrame">> & { readonly timelineEndFrame: number | null }): readonly SlipSlideConflict[] {
    const conflicts: SlipSlideConflict[] = [];
    if (!clip.clipId || !clip.trackId) conflicts.push(freezeConflict({ code: "missing-active-clip", message: "Active clip is required", clipId: clip.clipId || null, blocking: true }));
    if (!Number.isFinite(clip.timelineStartFrame) || !Number.isFinite(clip.timelineEndFrame) || clip.timelineEndFrame <= clip.timelineStartFrame) conflicts.push(freezeConflict({ code: "invalid-timeline-range", message: "Timeline range is invalid", clipId: clip.clipId, blocking: true }));
    if (!Number.isFinite(clip.sourceStartFrame) || !Number.isFinite(clip.sourceEndFrame) || !Number.isFinite(clip.sourceDurationFrames) || clip.sourceStartFrame < 0 || clip.sourceEndFrame <= clip.sourceStartFrame || clip.sourceEndFrame > clip.sourceDurationFrames) conflicts.push(freezeConflict({ code: "invalid-source-range", message: "Source range is invalid", clipId: clip.clipId, blocking: true }));
    if (clip.timelineEndFrame - clip.timelineStartFrame !== clip.sourceEndFrame - clip.sourceStartFrame) conflicts.push(freezeConflict({ code: "invalid-source-range", message: "Timeline and source durations must match", clipId: clip.clipId, blocking: true }));
    if (configuration.blockOnLockedClip && clip.locked) conflicts.push(freezeConflict({ code: "locked-active-clip", message: `Clip ${clip.clipId} is locked`, clipId: clip.clipId, blocking: true }));
    return Object.freeze(conflicts);
  }

  static calculate(
    clip: SlipSlideTimelineClip,
    requestedDeltaFrames: number,
    configuration: Required<Omit<TimelineSlipSlideConfiguration, "timelineEndFrame">> & { readonly timelineEndFrame: number | null },
  ): TimelineSlipPreview {
    const requested = Math.round(requestedDeltaFrames);
    const minimum = -clip.sourceStartFrame;
    const maximum = clip.sourceDurationFrames - clip.sourceEndFrame;
    const finite = Number.isFinite(requestedDeltaFrames);
    const resolved = finite && configuration.clampPreviewToValidRange ? Math.min(maximum, Math.max(minimum, requested)) : requested;
    const conflicts: SlipSlideConflict[] = [];
    if (!finite) conflicts.push(freezeConflict({ code: "invalid-delta", message: "Slip delta must be finite", clipId: clip.clipId, requestedDeltaFrames: null, blocking: true }));
    if (finite && requested < minimum) conflicts.push(freezeConflict({ code: "source-underflow", message: "Slip exceeds source start", clipId: clip.clipId, requestedDeltaFrames: requested, allowedDeltaFrames: minimum, blocking: !configuration.clampPreviewToValidRange }));
    if (finite && requested > maximum) conflicts.push(freezeConflict({ code: "source-overflow", message: "Slip exceeds source end", clipId: clip.clipId, requestedDeltaFrames: requested, allowedDeltaFrames: maximum, blocking: !configuration.clampPreviewToValidRange }));
    const blocked = conflicts.some((item) => item.blocking);
    const safeDelta = blocked ? 0 : resolved;
    return Object.freeze({
      operation: "slip",
      requestedDeltaFrames: finite ? requested : 0,
      resolvedDeltaFrames: safeDelta,
      original: freezePosition(clip),
      preview: freezePosition(clip, safeDelta),
      minimumDeltaFrames: minimum,
      maximumDeltaFrames: maximum,
      clamped: finite && safeDelta !== requested,
      blocked,
      conflicts: Object.freeze(conflicts),
    });
  }
}
