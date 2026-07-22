import type { TimelineSnapCandidate, TimelineSnapTarget, TimelineSnapTargetType } from "../contracts/magnetic-snap-contracts";
export const DEFAULT_TIMELINE_SNAP_PRIORITIES: Readonly<Record<TimelineSnapTargetType, number>> = Object.freeze({
  "timeline-start":1000,"timeline-end":950,playhead:900,marker:800,
  "clip-start":700,"clip-end":700,"subtitle-start":500,"subtitle-end":500,custom:400,
});
export function normalizeSnapTarget(target: TimelineSnapTarget, minFrame: number, maxFrame: number | null): TimelineSnapTarget | null {
  if (!target || typeof target.targetId !== "string" || !target.targetId.trim() || !Number.isFinite(target.frame)) return null;
  let frame=Math.round(target.frame); frame=Math.max(minFrame,frame); if(maxFrame!==null) frame=Math.min(maxFrame,frame);
  return Object.freeze({...target,targetId:target.targetId.trim(),frame,enabled:target.enabled!==false});
}
export function compareSnapCandidates(a: TimelineSnapCandidate,b: TimelineSnapCandidate): number {
  return b.effectivePriority-a.effectivePriority || a.absoluteDistanceFrames-b.absoluteDistanceFrames || a.targetFrame-b.targetFrame || a.targetId.localeCompare(b.targetId);
}
