import type { LinkableTimelineClip, TimelineLinkGroup, TimelineLinkMembership } from "../contracts/link-group-sync-contracts";
export class LinkGroupMembershipModel {
  static build(clips:readonly LinkableTimelineClip[], groups:readonly TimelineLinkGroup[]):readonly TimelineLinkMembership[]{
    const known=new Set(clips.map(c=>c.clipId)); const seen=new Set<string>(); const out:TimelineLinkMembership[]=[];
    for(const g of groups){ if(!g.clipIds.includes(g.anchorClipId)) throw new Error("anchor-not-in-group"); for(const id of g.clipIds){ if(!known.has(id)) throw new Error("unknown-group-member"); if(seen.has(id)) throw new Error("clip-in-multiple-groups"); seen.add(id); out.push(Object.freeze({clipId:id,groupId:g.groupId,role:id===g.anchorClipId?"anchor":"linked"})); } }
    return Object.freeze(out.sort((a,b)=>a.groupId.localeCompare(b.groupId)||Number(a.role!=="anchor")-Number(b.role!=="anchor")||a.clipId.localeCompare(b.clipId)));
  }
}
