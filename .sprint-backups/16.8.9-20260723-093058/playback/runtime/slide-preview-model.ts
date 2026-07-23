import type {
  SlipSlideClipPosition,
  SlipSlideConflict,
  SlipSlideTimelineClip,
  TimelineSlidePreview,
  TimelineSlipSlideConfiguration,
} from "../contracts/slip-slide-edit-contracts";

type NormalizedConfiguration = Required<Omit<TimelineSlipSlideConfiguration, "timelineEndFrame">> & { readonly timelineEndFrame: number | null };
export interface SlideSnapProjection { readonly resolvedDeltaFrames: number; readonly snapped: boolean; readonly targetId: string | null; readonly targetFrame: number | null; }
const conflict = (value: SlipSlideConflict): SlipSlideConflict => Object.freeze({ ...value });
const position = (clip: SlipSlideTimelineClip): SlipSlideClipPosition => Object.freeze({
  clipId: clip.clipId, trackId: clip.trackId,
  timelineStartFrame: clip.timelineStartFrame, timelineEndFrame: clip.timelineEndFrame,
  sourceStartFrame: clip.sourceStartFrame, sourceEndFrame: clip.sourceEndFrame,
});

export class SlidePreviewModel {
  static beginConflicts(previous: SlipSlideTimelineClip | null, active: SlipSlideTimelineClip, next: SlipSlideTimelineClip | null, configuration: NormalizedConfiguration): readonly SlipSlideConflict[] {
    const conflicts: SlipSlideConflict[] = [];
    if (!active.clipId || !active.trackId) conflicts.push(conflict({ code: "missing-active-clip", message: "Active clip is required", clipId: active.clipId || null, blocking: true }));
    if (!previous) conflicts.push(conflict({ code: "missing-previous-clip", message: "Previous clip is required", blocking: true }));
    if (!next) conflicts.push(conflict({ code: "missing-next-clip", message: "Next clip is required", blocking: true }));
    for (const clip of [previous, active, next]) {
      if (!clip) continue;
      if (clip.timelineEndFrame <= clip.timelineStartFrame) conflicts.push(conflict({ code: "invalid-timeline-range", message: `Clip ${clip.clipId} has invalid timeline range`, clipId: clip.clipId, blocking: true }));
      if (clip.sourceStartFrame < 0 || clip.sourceEndFrame <= clip.sourceStartFrame || clip.sourceEndFrame > clip.sourceDurationFrames) conflicts.push(conflict({ code: "invalid-source-range", message: `Clip ${clip.clipId} has invalid source range`, clipId: clip.clipId, blocking: true }));
      if (clip.timelineEndFrame - clip.timelineStartFrame !== clip.sourceEndFrame - clip.sourceStartFrame) conflicts.push(conflict({ code: "invalid-source-range", message: `Clip ${clip.clipId} timeline and source durations must match`, clipId: clip.clipId, blocking: true }));
    }
    if (previous && next && (previous.trackId !== active.trackId || next.trackId !== active.trackId)) conflicts.push(conflict({ code: "track-mismatch", message: "Slide clips must share one track", clipId: active.clipId, blocking: true }));
    if (configuration.requireContiguousNeighbors && previous && next && (previous.timelineEndFrame !== active.timelineStartFrame || active.timelineEndFrame !== next.timelineStartFrame)) conflicts.push(conflict({ code: "non-contiguous-neighbors", message: "Slide neighbors must be contiguous", clipId: active.clipId, blocking: true }));
    if (configuration.blockOnLockedClip) {
      if (active.locked) conflicts.push(conflict({ code: "locked-active-clip", message: `Clip ${active.clipId} is locked`, clipId: active.clipId, blocking: true }));
      if (previous?.locked) conflicts.push(conflict({ code: "locked-previous-clip", message: `Clip ${previous.clipId} is locked`, clipId: previous.clipId, blocking: true }));
      if (next?.locked) conflicts.push(conflict({ code: "locked-next-clip", message: `Clip ${next.clipId} is locked`, clipId: next.clipId, blocking: true }));
    }
    return Object.freeze(conflicts);
  }

  static calculate(previous: SlipSlideTimelineClip, active: SlipSlideTimelineClip, next: SlipSlideTimelineClip, requestedDeltaFrames: number, configuration: NormalizedConfiguration, snap?: SlideSnapProjection): TimelineSlidePreview {
    const requested = Math.round(requestedDeltaFrames);
    const snappedRequested = snap ? Math.round(snap.resolvedDeltaFrames) : requested;
    const previousDuration = previous.timelineEndFrame - previous.timelineStartFrame;
    const nextDuration = next.timelineEndFrame - next.timelineStartFrame;
    const minimum = Math.max(
      configuration.minimumClipDurationFrames - previousDuration,
      -next.sourceStartFrame,
      configuration.timelineStartFrame - active.timelineStartFrame,
    );
    const maximumValues = [
      nextDuration - configuration.minimumClipDurationFrames,
      previous.sourceDurationFrames - previous.sourceEndFrame,
    ];
    if (configuration.timelineEndFrame !== null) maximumValues.push(configuration.timelineEndFrame - active.timelineEndFrame);
    const maximum = Math.min(...maximumValues);
    const finite = Number.isFinite(requestedDeltaFrames) && Number.isFinite(snappedRequested);
    const resolved = finite && configuration.clampPreviewToValidRange ? Math.min(maximum, Math.max(minimum, snappedRequested)) : snappedRequested;
    const conflicts: SlipSlideConflict[] = [];
    if (!finite || minimum > maximum) conflicts.push(conflict({ code: "invalid-delta", message: "Slide delta is invalid", clipId: active.clipId, blocking: true }));
    if (finite && snappedRequested < minimum) {
      const code = snappedRequested < configuration.timelineStartFrame - active.timelineStartFrame ? "timeline-underflow" : snappedRequested < -next.sourceStartFrame ? "source-underflow" : "minimum-duration-violation";
      conflicts.push(conflict({ code, message: "Slide is below the valid range", clipId: active.clipId, requestedDeltaFrames: snappedRequested, allowedDeltaFrames: minimum, blocking: !configuration.clampPreviewToValidRange }));
    }
    if (finite && snappedRequested > maximum) {
      const timelineLimit = configuration.timelineEndFrame === null ? Number.POSITIVE_INFINITY : configuration.timelineEndFrame - active.timelineEndFrame;
      const code = snappedRequested > timelineLimit ? "timeline-overflow" : snappedRequested > previous.sourceDurationFrames - previous.sourceEndFrame ? "source-overflow" : "minimum-duration-violation";
      conflicts.push(conflict({ code, message: "Slide is above the valid range", clipId: active.clipId, requestedDeltaFrames: snappedRequested, allowedDeltaFrames: maximum, blocking: !configuration.clampPreviewToValidRange }));
    }
    const blocked = conflicts.some((item) => item.blocking);
    const delta = blocked ? 0 : resolved;
    const previousPreview = Object.freeze({ ...position(previous), timelineEndFrame: previous.timelineEndFrame + delta, sourceEndFrame: previous.sourceEndFrame + delta });
    const activePreview = Object.freeze({ ...position(active), timelineStartFrame: active.timelineStartFrame + delta, timelineEndFrame: active.timelineEndFrame + delta });
    const nextPreview = Object.freeze({ ...position(next), timelineStartFrame: next.timelineStartFrame + delta, sourceStartFrame: next.sourceStartFrame + delta });
    if (!blocked) {
      if (previousPreview.timelineEndFrame < activePreview.timelineStartFrame || activePreview.timelineEndFrame < nextPreview.timelineStartFrame) conflicts.push(conflict({ code: "gap-detected", message: "Slide created a gap", clipId: active.clipId, blocking: true }));
      if (previousPreview.timelineEndFrame > activePreview.timelineStartFrame || activePreview.timelineEndFrame > nextPreview.timelineStartFrame) conflicts.push(conflict({ code: "overlap-detected", message: "Slide created an overlap", clipId: active.clipId, blocking: true }));
    }
    const finalBlocked = conflicts.some((item) => item.blocking);
    return Object.freeze({
      operation: "slide", requestedDeltaFrames: finite ? requested : 0, resolvedDeltaFrames: finalBlocked ? 0 : delta,
      previousOriginal: position(previous), activeOriginal: position(active), nextOriginal: position(next),
      previousPreview: finalBlocked ? position(previous) : previousPreview,
      activePreview: finalBlocked ? position(active) : activePreview,
      nextPreview: finalBlocked ? position(next) : nextPreview,
      minimumDeltaFrames: minimum, maximumDeltaFrames: maximum,
      clamped: finite && !finalBlocked && delta !== snappedRequested, blocked: finalBlocked,
      conflicts: Object.freeze(conflicts), snapped: Boolean(snap?.snapped), snapTargetId: snap?.targetId ?? null, snapTargetFrame: snap?.targetFrame ?? null,
    });
  }
}
