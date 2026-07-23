import type {
  RippleClipPosition,
  RippleConflict,
  RippleEditOperation,
  RippleTimelineClip,
  TimelineRippleConfiguration,
} from "../contracts/ripple-edit-contracts";

export interface RippleCalculation {
  readonly deltaFrames: number;
  readonly affectedClipIds: readonly string[];
  readonly positions: readonly RippleClipPosition[];
  readonly conflicts: readonly RippleConflict[];
}

const freezePosition = (clip: RippleTimelineClip, shift = 0): RippleClipPosition => Object.freeze({
  clipId: clip.clipId,
  trackId: clip.trackId,
  timelineStartFrame: clip.timelineStartFrame + shift,
  timelineEndFrame: clip.timelineEndFrame + shift,
  sourceStartFrame: clip.sourceStartFrame,
  sourceEndFrame: clip.sourceEndFrame,
  shiftedByFrames: shift,
});

export class RipplePreviewModel {
  static normalizeClips(clips: readonly RippleTimelineClip[]): RippleTimelineClip[] {
    const byId = new Map<string, RippleTimelineClip>();
    for (const clip of clips) {
      if (!clip.clipId || !clip.trackId) continue;
      byId.set(clip.clipId, Object.freeze({
        clipId: clip.clipId,
        trackId: clip.trackId,
        timelineStartFrame: Math.round(clip.timelineStartFrame),
        timelineEndFrame: Math.round(clip.timelineEndFrame),
        sourceStartFrame: Math.round(clip.sourceStartFrame),
        sourceEndFrame: Math.round(clip.sourceEndFrame),
        locked: Boolean(clip.locked),
      }));
    }
    return [...byId.values()].sort((a, b) =>
      a.trackId.localeCompare(b.trackId) || a.timelineStartFrame - b.timelineStartFrame || a.clipId.localeCompare(b.clipId));
  }

  static origin(clips: readonly RippleTimelineClip[]): readonly RippleClipPosition[] {
    return Object.freeze(clips.map((clip) => freezePosition(clip)));
  }

  static calculate(
    clips: readonly RippleTimelineClip[],
    anchor: RippleTimelineClip,
    operation: Exclude<RippleEditOperation, "delete-gap">,
    requestedDeltaFrames: number,
    configuration: Required<TimelineRippleConfiguration>,
  ): RippleCalculation {
    const deltaFrames = Math.round(requestedDeltaFrames);
    const sameTrack = clips.filter((clip) => clip.trackId === anchor.trackId);
    const boundary = operation === "trim-start" ? anchor.timelineStartFrame : anchor.timelineEndFrame;
    const affected = sameTrack.filter((clip) => clip.clipId !== anchor.clipId && clip.timelineStartFrame >= boundary);
    const positions = clips.map((clip) => {
      if (clip.clipId === anchor.clipId) {
        if (operation === "move") return freezePosition(clip, deltaFrames);
        if (operation === "trim-start") return Object.freeze({
          ...freezePosition(clip),
          timelineStartFrame: clip.timelineStartFrame + deltaFrames,
          sourceStartFrame: clip.sourceStartFrame + deltaFrames,
          shiftedByFrames: 0,
        });
        return Object.freeze({
          ...freezePosition(clip),
          timelineEndFrame: clip.timelineEndFrame + deltaFrames,
          sourceEndFrame: clip.sourceEndFrame + deltaFrames,
          shiftedByFrames: 0,
        });
      }
      const shouldShift = affected.some((item) => item.clipId === clip.clipId);
      return freezePosition(clip, shouldShift ? deltaFrames : 0);
    });
    return this.validate(positions, affected.map((clip) => clip.clipId), deltaFrames, clips, configuration);
  }

  static deleteGap(
    clips: readonly RippleTimelineClip[],
    trackId: string,
    gapStartFrame: number,
    gapEndFrame: number,
    configuration: Required<TimelineRippleConfiguration>,
  ): RippleCalculation {
    const start = Math.round(gapStartFrame);
    const end = Math.round(gapEndFrame);
    if (end <= start) {
      return Object.freeze({ deltaFrames: 0, affectedClipIds: Object.freeze([]), positions: this.origin(clips), conflicts: Object.freeze([{ type: "invalid-gap" as const, clipId: null, message: "Gap end must be greater than gap start" }]) });
    }
    const deltaFrames = start - end;
    const affected = clips.filter((clip) => clip.trackId === trackId && clip.timelineStartFrame >= end);
    const positions = clips.map((clip) => freezePosition(clip, affected.some((item) => item.clipId === clip.clipId) ? deltaFrames : 0));
    return this.validate(positions, affected.map((clip) => clip.clipId), deltaFrames, clips, configuration);
  }

  private static validate(
    positions: readonly RippleClipPosition[],
    affectedClipIds: readonly string[],
    deltaFrames: number,
    originalClips: readonly RippleTimelineClip[],
    configuration: Required<TimelineRippleConfiguration>,
  ): RippleCalculation {
    const conflicts: RippleConflict[] = [];
    const affected = new Set(affectedClipIds);
    if (configuration.blockOnLockedClip) {
      for (const clip of originalClips) if (affected.has(clip.clipId) && clip.locked) conflicts.push(Object.freeze({ type: "locked-clip", clipId: clip.clipId, message: `Locked clip ${clip.clipId} cannot be rippled` }));
    }
    for (const position of positions) {
      if (position.timelineEndFrame <= position.timelineStartFrame || position.sourceEndFrame <= position.sourceStartFrame) conflicts.push(Object.freeze({ type: "invalid-duration", clipId: position.clipId, message: `Clip ${position.clipId} has invalid duration` }));
      if (position.timelineStartFrame < configuration.timelineStartFrame) conflicts.push(Object.freeze({ type: "timeline-underflow", clipId: position.clipId, message: `Clip ${position.clipId} is before timeline start` }));
      if (position.timelineEndFrame > configuration.timelineEndFrame) conflicts.push(Object.freeze({ type: "timeline-overflow", clipId: position.clipId, message: `Clip ${position.clipId} exceeds timeline end` }));
    }
    if (configuration.preventOverlap) {
      const tracks = new Map<string, RippleClipPosition[]>();
      for (const position of positions) tracks.set(position.trackId, [...(tracks.get(position.trackId) ?? []), position]);
      for (const items of tracks.values()) {
        items.sort((a, b) => a.timelineStartFrame - b.timelineStartFrame || a.clipId.localeCompare(b.clipId));
        for (let index = 1; index < items.length; index += 1) {
          if (items[index].timelineStartFrame < items[index - 1].timelineEndFrame) conflicts.push(Object.freeze({ type: "overlap", clipId: items[index].clipId, message: `Clip ${items[index].clipId} overlaps ${items[index - 1].clipId}` }));
        }
      }
    }
    return Object.freeze({
      deltaFrames,
      affectedClipIds: Object.freeze([...affectedClipIds]),
      positions: Object.freeze(positions.map((position) => Object.freeze({ ...position }))),
      conflicts: Object.freeze(conflicts),
    });
  }
}
