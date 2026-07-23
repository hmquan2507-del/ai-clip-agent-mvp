import type {
  RollClipPosition,
  RollTimelineClip,
  TimelineRollConflict,
  TimelineRollEditConfiguration,
  TimelineRollPreview,
} from "../contracts/roll-edit-contracts";

export type NormalizedRollConfiguration = Required<Omit<TimelineRollEditConfiguration, "timelineEndFrame">> & { readonly timelineEndFrame: number | null };
export interface RollSnapProjection { readonly resolvedCutFrame: number; readonly snapped: boolean; readonly targetId: string | null; readonly targetFrame: number | null; }
const conflict = (code: TimelineRollConflict["code"], message: string, clipId?: string | null, requested?: number | null, allowed?: number | null): TimelineRollConflict => Object.freeze({ code, message, clipId, requestedDeltaFrames: requested, allowedDeltaFrames: allowed, blocking: true });
const position = (clip: RollTimelineClip): RollClipPosition => Object.freeze({ clipId: clip.clipId, trackId: clip.trackId, timelineStartFrame: clip.timelineStartFrame, timelineEndFrame: clip.timelineEndFrame, sourceStartFrame: clip.sourceStartFrame, sourceEndFrame: clip.sourceEndFrame });
const freezeConflicts = (items: readonly TimelineRollConflict[]) => Object.freeze(items.map((item) => Object.freeze({ ...item })));

export class RollPreviewModel {
  static normalizeClip(clip: RollTimelineClip): RollTimelineClip {
    return Object.freeze({ ...clip, clipId: String(clip.clipId ?? "").trim(), trackId: String(clip.trackId ?? "").trim(), timelineStartFrame: Math.round(clip.timelineStartFrame), timelineEndFrame: Math.round(clip.timelineEndFrame), sourceStartFrame: Math.round(clip.sourceStartFrame), sourceEndFrame: Math.round(clip.sourceEndFrame), sourceDurationFrames: Math.round(clip.sourceDurationFrames), locked: clip.locked === true });
  }

  static beginConflicts(left: RollTimelineClip | null, right: RollTimelineClip | null, config: NormalizedRollConfiguration): readonly TimelineRollConflict[] {
    const out: TimelineRollConflict[] = [];
    if (!left) out.push(conflict("missing-left-clip", "Left clip is required"));
    if (!right) out.push(conflict("missing-right-clip", "Right clip is required"));
    if (!left || !right) return freezeConflicts(out);
    if (left.trackId !== right.trackId) out.push(conflict("track-mismatch", "Roll clips must be on the same track"));
    if (config.requireContiguousClips && left.timelineEndFrame !== right.timelineStartFrame) out.push(conflict("non-contiguous-clips", "Roll clips must share a contiguous cut"));
    if (config.blockOnLockedClip && left.locked) out.push(conflict("locked-left-clip", "Left clip is locked", left.clipId));
    if (config.blockOnLockedClip && right.locked) out.push(conflict("locked-right-clip", "Right clip is locked", right.clipId));
    if (!left.clipId || !Number.isFinite(left.timelineStartFrame) || !Number.isFinite(left.timelineEndFrame) || left.timelineEndFrame <= left.timelineStartFrame) out.push(conflict("invalid-left-timeline-range", "Left timeline range is invalid", left.clipId));
    if (!right.clipId || !Number.isFinite(right.timelineStartFrame) || !Number.isFinite(right.timelineEndFrame) || right.timelineEndFrame <= right.timelineStartFrame) out.push(conflict("invalid-right-timeline-range", "Right timeline range is invalid", right.clipId));
    if (!Number.isFinite(left.sourceStartFrame) || !Number.isFinite(left.sourceEndFrame) || !Number.isFinite(left.sourceDurationFrames) || left.sourceStartFrame < 0 || left.sourceEndFrame <= left.sourceStartFrame || left.sourceEndFrame > left.sourceDurationFrames) out.push(conflict("invalid-left-source-range", "Left source range is invalid", left.clipId));
    if (!Number.isFinite(right.sourceStartFrame) || !Number.isFinite(right.sourceEndFrame) || !Number.isFinite(right.sourceDurationFrames) || right.sourceStartFrame < 0 || right.sourceEndFrame <= right.sourceStartFrame || right.sourceEndFrame > right.sourceDurationFrames) out.push(conflict("invalid-right-source-range", "Right source range is invalid", right.clipId));
    if ((left.timelineEndFrame-left.timelineStartFrame)!==(left.sourceEndFrame-left.sourceStartFrame) || (right.timelineEndFrame-right.timelineStartFrame)!==(right.sourceEndFrame-right.sourceStartFrame)) out.push(conflict("duration-mismatch", "Timeline and source durations must match"));
    const [min,max]=this.deltaRange(left,right,config);
    if (min>max) out.push(conflict("invalid-roll-range", "No valid roll delta is available"));
    return freezeConflicts(out);
  }

  static deltaRange(left: RollTimelineClip, right: RollTimelineClip, config: NormalizedRollConfiguration): readonly [number, number] {
    const leftDuration=left.timelineEndFrame-left.timelineStartFrame;
    const rightDuration=right.timelineEndFrame-right.timelineStartFrame;
    let minimum=Math.max(config.minimumClipDurationFrames-leftDuration,-right.sourceStartFrame,config.timelineStartFrame-left.timelineEndFrame);
    let maximum=Math.min(rightDuration-config.minimumClipDurationFrames,left.sourceDurationFrames-left.sourceEndFrame);
    if(config.timelineEndFrame!==null) maximum=Math.min(maximum,config.timelineEndFrame-left.timelineEndFrame);
    return Object.freeze([Math.ceil(minimum),Math.floor(maximum)]);
  }

  static calculate(left: RollTimelineClip, right: RollTimelineClip, requestedDeltaFrames: number, config: NormalizedRollConfiguration, snap?: RollSnapProjection): TimelineRollPreview {
    const requested=Number.isFinite(requestedDeltaFrames)?Math.round(requestedDeltaFrames):requestedDeltaFrames;
    const originalCut=left.timelineEndFrame;
    const snappedCut=snap?.resolvedCutFrame ?? (Number.isFinite(requested)?originalCut+requested:requested);
    const snappedDelta=Number.isFinite(snappedCut)?Math.round(snappedCut)-originalCut:snappedCut;
    const [minimum,maximum]=this.deltaRange(left,right,config);
    const issues: TimelineRollConflict[]=[];
    let resolved=snappedDelta; let blocked=false; let clamped=false;
    if(!Number.isFinite(snappedDelta)){issues.push(conflict("invalid-delta","Roll delta must be finite",null,requested,null));blocked=true;}
    else if(snappedDelta<minimum || snappedDelta>maximum){
      if(config.clampPreviewToValidRange){resolved=Math.max(minimum,Math.min(snappedDelta,maximum));clamped=resolved!==snappedDelta;}
      else {blocked=true; if(snappedDelta<minimum) issues.push(conflict(this.lowerCode(left,right,config,snappedDelta),"Roll delta is below the valid range",null,snappedDelta,minimum)); else issues.push(conflict(this.upperCode(left,right,config,snappedDelta),"Roll delta is above the valid range",null,snappedDelta,maximum));}
    }
    const safe=Number.isFinite(resolved)?resolved:0;
    const leftPreview=Object.freeze({ ...position(left), timelineEndFrame:left.timelineEndFrame+safe, sourceEndFrame:left.sourceEndFrame+safe });
    const rightPreview=Object.freeze({ ...position(right), timelineStartFrame:right.timelineStartFrame+safe, sourceStartFrame:right.sourceStartFrame+safe });
    if(leftPreview.timelineEndFrame<rightPreview.timelineStartFrame) issues.push(conflict("gap-detected","Roll preview created a gap"));
    if(leftPreview.timelineEndFrame>rightPreview.timelineStartFrame) issues.push(conflict("overlap-detected","Roll preview created an overlap"));
    return Object.freeze({ requestedDeltaFrames:requested, resolvedDeltaFrames:resolved, originalCutFrame:originalCut, previewCutFrame:originalCut+safe, leftOriginal:position(left), rightOriginal:position(right), leftPreview, rightPreview, minimumDeltaFrames:minimum, maximumDeltaFrames:maximum, snapped:snap?.snapped===true, snapTargetId:snap?.targetId??null, snapTargetFrame:snap?.targetFrame??null, clamped, blocked:blocked||issues.some(i=>i.blocking), conflicts:freezeConflicts(issues) });
  }

  private static lowerCode(left:RollTimelineClip,right:RollTimelineClip,config:NormalizedRollConfiguration,delta:number):TimelineRollConflict["code"]{
    if(left.timelineEndFrame+delta<config.timelineStartFrame)return "timeline-underflow";
    if(right.sourceStartFrame+delta<0)return "right-source-underflow";
    return "left-minimum-duration-violation";
  }
  private static upperCode(left:RollTimelineClip,right:RollTimelineClip,config:NormalizedRollConfiguration,delta:number):TimelineRollConflict["code"]{
    if(config.timelineEndFrame!==null&&left.timelineEndFrame+delta>config.timelineEndFrame)return "timeline-overflow";
    if(left.sourceEndFrame+delta>left.sourceDurationFrames)return "left-source-overflow";
    return "right-minimum-duration-violation";
  }
}
