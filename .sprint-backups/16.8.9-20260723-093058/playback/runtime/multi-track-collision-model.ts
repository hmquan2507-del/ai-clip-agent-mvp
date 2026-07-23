import type { MultiTrackClipPosition, MultiTrackCollision, MultiTrackTimelineClip } from "../contracts/multi-track-edit-contracts";

export class MultiTrackCollisionModel {
  static detect(clips:readonly MultiTrackTimelineClip[],preview:ReadonlyMap<string,MultiTrackClipPosition>,timelineStart:number,timelineEnd:number|null):readonly MultiTrackCollision[]{
    const byTrack=new Map<string,MultiTrackClipPosition[]>();
    for(const clip of clips){const pos=preview.get(clip.clipId)??this.position(clip);const list=byTrack.get(pos.trackId)??[];list.push(pos);byTrack.set(pos.trackId,list);}
    const out:MultiTrackCollision[]=[];
    for(const [trackId,positions] of byTrack){
      const sorted=[...positions].sort((a,b)=>a.timelineStartFrame-b.timelineStartFrame||a.timelineEndFrame-b.timelineEndFrame||a.clipId.localeCompare(b.clipId));
      for(const p of sorted){if(p.timelineStartFrame<timelineStart)out.push(this.item("timeline-underflow",trackId,p));if(timelineEnd!==null&&p.timelineEndFrame>timelineEnd)out.push(this.item("timeline-overflow",trackId,p));}
      for(let i=0;i<sorted.length-1;i++){const a=sorted[i],b=sorted[i+1];if(a&&b&&a.timelineEndFrame>b.timelineStartFrame)out.push(Object.freeze({kind:"overlap",trackId,clipId:a.clipId,conflictingClipId:b.clipId,startFrame:b.timelineStartFrame,endFrame:Math.min(a.timelineEndFrame,b.timelineEndFrame),blocking:true}));}
    }
    return Object.freeze(out);
  }
  static position(c:MultiTrackTimelineClip):MultiTrackClipPosition{return Object.freeze({clipId:c.clipId,trackId:c.trackId,timelineStartFrame:c.timelineStartFrame,timelineEndFrame:c.timelineEndFrame,sourceStartFrame:c.sourceStartFrame??null,sourceEndFrame:c.sourceEndFrame??null});}
  private static item(kind:"timeline-underflow"|"timeline-overflow",trackId:string,p:MultiTrackClipPosition):MultiTrackCollision{return Object.freeze({kind,trackId,clipId:p.clipId,startFrame:p.timelineStartFrame,endFrame:p.timelineEndFrame,blocking:true});}
}
