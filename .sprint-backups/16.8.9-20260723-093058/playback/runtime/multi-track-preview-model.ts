import type { MultiTrackChangeKind, MultiTrackClipChange, MultiTrackClipPosition, MultiTrackTimelineClip, TimelineMultiTrackConflict } from "../contracts/multi-track-edit-contracts";

const pos=(c:MultiTrackTimelineClip):MultiTrackClipPosition=>Object.freeze({clipId:c.clipId,trackId:c.trackId,timelineStartFrame:c.timelineStartFrame,timelineEndFrame:c.timelineEndFrame,sourceStartFrame:c.sourceStartFrame??null,sourceEndFrame:c.sourceEndFrame??null});
export class MultiTrackPreviewModel {
  static change(clip:MultiTrackTimelineClip,kind:MultiTrackChangeKind,delta:number,minimumDuration:number):{change:MultiTrackClipChange;conflicts:readonly TimelineMultiTrackConflict[]} {
    const original=pos(clip);let start=original.timelineStartFrame,end=original.timelineEndFrame,sourceStart=original.sourceStartFrame,sourceEnd=original.sourceEndFrame;
    if(kind==="moved"||kind==="ripple-shifted"){start+=delta;end+=delta;}
    else if(kind==="trimmed-start"){start+=delta;if(sourceStart!==null)sourceStart+=delta;}
    else if(kind==="trimmed-end"){end+=delta;if(sourceEnd!==null)sourceEnd+=delta;}
    const conflicts:TimelineMultiTrackConflict[]=[];
    if(end-start<minimumDuration)conflicts.push(Object.freeze({code:"minimum-duration-violation",message:"Preview violates minimum clip duration",clipId:clip.clipId,trackId:clip.trackId,blocking:true}));
    if(sourceStart!==null&&sourceStart<0)conflicts.push(Object.freeze({code:"invalid-source-range",message:"Source start is below zero",clipId:clip.clipId,trackId:clip.trackId,blocking:true}));
    if(sourceEnd!==null&&clip.sourceDurationFrames!=null&&sourceEnd>clip.sourceDurationFrames)conflicts.push(Object.freeze({code:"invalid-source-range",message:"Source end exceeds source duration",clipId:clip.clipId,trackId:clip.trackId,blocking:true}));
    const preview=Object.freeze({clipId:clip.clipId,trackId:clip.trackId,timelineStartFrame:start,timelineEndFrame:end,sourceStartFrame:sourceStart,sourceEndFrame:sourceEnd});
    return {change:Object.freeze({clipId:clip.clipId,trackId:clip.trackId,kind,original,preview,deltaFrames:delta}),conflicts:Object.freeze(conflicts)};
  }
}
