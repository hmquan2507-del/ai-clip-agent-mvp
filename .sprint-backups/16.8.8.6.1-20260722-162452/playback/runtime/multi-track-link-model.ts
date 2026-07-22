import type { MultiTrackDescriptor, MultiTrackLinkGroup, MultiTrackSyncRelation, MultiTrackTimelineClip } from "../contracts/multi-track-edit-contracts";

const frozenStrings=(items:readonly string[])=>Object.freeze([...new Set(items)].sort());
export class MultiTrackLinkModel {
  static build(tracks:readonly MultiTrackDescriptor[],clips:readonly MultiTrackTimelineClip[],preferredAnchorId?:string|null):{linkGroups:readonly MultiTrackLinkGroup[];syncRelations:readonly MultiTrackSyncRelation[]} {
    const trackById=new Map(tracks.map(t=>[t.trackId,t]));
    const groups=new Map<string,MultiTrackTimelineClip[]>();
    for(const clip of clips){if(!clip.linkGroupId)continue;const list=groups.get(clip.linkGroupId)??[];list.push(clip);groups.set(clip.linkGroupId,list);}
    const linkGroups:MultiTrackLinkGroup[]=[];const syncRelations:MultiTrackSyncRelation[]=[];
    for(const [id,members] of [...groups].sort(([a],[b])=>a.localeCompare(b))){
      const sorted=[...members].sort((a,b)=>this.anchorRank(a,preferredAnchorId,trackById)-this.anchorRank(b,preferredAnchorId,trackById)||a.clipId.localeCompare(b.clipId));
      const anchor=sorted[0];if(!anchor)continue;
      linkGroups.push(Object.freeze({linkGroupId:id,clipIds:frozenStrings(members.map(c=>c.clipId)),anchorClipId:anchor.clipId,minimumStartFrame:Math.min(...members.map(c=>c.timelineStartFrame)),maximumEndFrame:Math.max(...members.map(c=>c.timelineEndFrame))}));
      for(const clip of members){if(clip.clipId!==anchor.clipId)syncRelations.push(Object.freeze({anchorClipId:anchor.clipId,linkedClipId:clip.clipId,offsetFrames:clip.timelineStartFrame-anchor.timelineStartFrame}));}
    }
    return {linkGroups:Object.freeze(linkGroups),syncRelations:Object.freeze(syncRelations)};
  }
  private static anchorRank(clip:MultiTrackTimelineClip,preferred:string|null|undefined,trackById:Map<string,MultiTrackDescriptor>):number{
    if(clip.clipId===preferred)return -100000;
    const track=trackById.get(clip.trackId);const kind=track?.kind;
    const kindRank=kind==="video"?0:kind==="audio"?1000:2000;
    return kindRank+(track?.order??99999);
  }
}
