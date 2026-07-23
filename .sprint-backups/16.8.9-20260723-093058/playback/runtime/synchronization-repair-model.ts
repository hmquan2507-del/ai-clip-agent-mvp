import type { LinkableTimelineClip, TimelineSyncRelation, TimelineSyncRepairChange, TimelineSyncRepairStrategy } from "../contracts/link-group-sync-contracts";
export class SynchronizationRepairModel {
  static build(clips:readonly LinkableTimelineClip[], relations:readonly TimelineSyncRelation[], strategy:TimelineSyncRepairStrategy):readonly TimelineSyncRepairChange[]{
    if(strategy==="ignore"||strategy==="recapture-current-offset") return Object.freeze([]);
    const byId=new Map(clips.map(c=>[c.clipId,c])); const out:TimelineSyncRepairChange[]=[];
    for(const r of relations){const a=byId.get(r.anchorClipId),l=byId.get(r.linkedClipId); if(!a||!l||!r.enabled) continue; const expected=a.timelineStartFrame+r.timelineStartOffsetFrames; const delta=expected-l.timelineStartFrame; if(!delta) continue; const target=strategy==="move-anchor-to-linked"?a:l; const applied=strategy==="move-anchor-to-linked"?-delta:delta; out.push(Object.freeze({clipId:target.clipId,trackId:target.trackId,originalStartFrame:target.timelineStartFrame,originalEndFrame:target.timelineEndFrame,previewStartFrame:target.timelineStartFrame+applied,previewEndFrame:target.timelineEndFrame+applied,deltaFrames:applied,reason:`repair:${r.relationId}`})); }
    return Object.freeze(out.sort((a,b)=>a.trackId.localeCompare(b.trackId)||a.originalStartFrame-b.originalStartFrame||a.clipId.localeCompare(b.clipId)));
  }
}
