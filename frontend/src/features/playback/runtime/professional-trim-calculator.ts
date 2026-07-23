import type { ProfessionalTrimClip, ProfessionalTrimConflict, ProfessionalTrimMode, ProfessionalTrimPosition } from "../contracts/professional-trim-contracts";

export interface ProfessionalTrimLimits { readonly minimumDurationFrames: number; readonly timelineStartFrame: number; readonly timelineEndFrame: number | null; readonly blockOnLockedClip: boolean; }

const position = (clip: ProfessionalTrimClip, patch: Partial<ProfessionalTrimPosition> = {}): ProfessionalTrimPosition => Object.freeze({ ...clip, shiftedByFrames: 0, ...patch });

export class ProfessionalTrimCalculator {
  static calculate(clips: readonly ProfessionalTrimClip[], mode: ProfessionalTrimMode, activeId: string, secondaryId: string | null, delta: number, limits: ProfessionalTrimLimits): { positions: readonly ProfessionalTrimPosition[]; resolvedDeltaFrames: number; conflicts: readonly ProfessionalTrimConflict[] } {
    const normalized = Number.isFinite(delta) ? Math.round(delta) : 0;
    const active = clips.find((clip) => clip.clipId === activeId);
    const secondary = secondaryId ? clips.find((clip) => clip.clipId === secondaryId) : undefined;
    const conflicts: ProfessionalTrimConflict[] = [];
    if (!active) return { positions: Object.freeze(clips.map((clip) => position(clip))), resolvedDeltaFrames: 0, conflicts: Object.freeze([{ code: "missing-clip", message: `Active clip ${activeId} was not found`, clipId: activeId, blocking: true }]) };
    if (limits.blockOnLockedClip && active.locked) conflicts.push({ code: "locked-clip", message: `Clip ${active.clipId} is locked`, clipId: active.clipId, blocking: true });
    if ((mode === "roll" || mode === "slide") && !secondary) conflicts.push({ code: "invalid-neighbor", message: `${mode} edit requires a secondary clip`, clipId: secondaryId, blocking: true });
    if (secondary && limits.blockOnLockedClip && secondary.locked) conflicts.push({ code: "locked-clip", message: `Clip ${secondary.clipId} is locked`, clipId: secondary.clipId, blocking: true });
    if (conflicts.some((item) => item.blocking)) return { positions: Object.freeze(clips.map((clip) => position(clip))), resolvedDeltaFrames: 0, conflicts: Object.freeze(conflicts) };

    let resolved = normalized;
    const duration = active.timelineEndFrame - active.timelineStartFrame;
    if (mode === "ripple-start") resolved = Math.max(active.sourceStartFrame * -1, Math.min(resolved, duration - limits.minimumDurationFrames));
    if (mode === "ripple-end") resolved = Math.max(limits.minimumDurationFrames - duration, Math.min(resolved, active.sourceDurationFrames - active.sourceEndFrame));
    if (mode === "slip") resolved = Math.max(-active.sourceStartFrame, Math.min(resolved, active.sourceDurationFrames - active.sourceEndFrame));
    if (mode === "roll" && secondary) {
      const leftDuration = active.timelineEndFrame - active.timelineStartFrame;
      const rightDuration = secondary.timelineEndFrame - secondary.timelineStartFrame;
      resolved = Math.max(limits.minimumDurationFrames - leftDuration, Math.min(resolved, rightDuration - limits.minimumDurationFrames));
      resolved = Math.max(-active.sourceEndFrame, Math.min(resolved, secondary.sourceStartFrame));
    }
    if (mode === "slide" && secondary) {
      const minTimeline = limits.timelineStartFrame - active.timelineStartFrame;
      const maxTimeline = limits.timelineEndFrame == null ? Number.MAX_SAFE_INTEGER : limits.timelineEndFrame - active.timelineEndFrame;
      resolved = Math.max(minTimeline, Math.min(resolved, maxTimeline));
    }

    const activeTrack = active.trackId;
    const result = clips.map((clip) => {
      if (mode === "ripple-start") {
        if (clip.clipId === active.clipId) return position(clip, { timelineStartFrame: clip.timelineStartFrame + resolved, sourceStartFrame: clip.sourceStartFrame + resolved });
        return position(clip);
      }
      if (mode === "ripple-end") {
        if (clip.clipId === active.clipId) return position(clip, { timelineEndFrame: clip.timelineEndFrame + resolved, sourceEndFrame: clip.sourceEndFrame + resolved });
        if (clip.trackId === activeTrack && clip.timelineStartFrame >= active.timelineEndFrame) return position(clip, { timelineStartFrame: clip.timelineStartFrame + resolved, timelineEndFrame: clip.timelineEndFrame + resolved, shiftedByFrames: resolved });
        return position(clip);
      }
      if (mode === "slip") return clip.clipId === active.clipId ? position(clip, { sourceStartFrame: clip.sourceStartFrame + resolved, sourceEndFrame: clip.sourceEndFrame + resolved }) : position(clip);
      if (mode === "roll" && secondary) {
        if (clip.clipId === active.clipId) return position(clip, { timelineEndFrame: clip.timelineEndFrame + resolved, sourceEndFrame: clip.sourceEndFrame + resolved });
        if (clip.clipId === secondary.clipId) return position(clip, { timelineStartFrame: clip.timelineStartFrame + resolved, sourceStartFrame: clip.sourceStartFrame + resolved });
        return position(clip);
      }
      if (mode === "slide" && secondary) {
        if (clip.clipId === active.clipId) return position(clip, { timelineStartFrame: clip.timelineStartFrame + resolved, timelineEndFrame: clip.timelineEndFrame + resolved, shiftedByFrames: resolved });
        if (clip.clipId === secondary.clipId) return position(clip, { timelineEndFrame: clip.timelineEndFrame + resolved, sourceEndFrame: clip.sourceEndFrame + resolved });
        return position(clip);
      }
      return position(clip);
    });
    return { positions: Object.freeze(result), resolvedDeltaFrames: resolved, conflicts: Object.freeze(conflicts) };
  }
}
