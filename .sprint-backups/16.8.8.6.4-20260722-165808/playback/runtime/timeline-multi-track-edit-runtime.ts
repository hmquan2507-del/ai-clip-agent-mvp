import {
  TIMELINE_MULTI_TRACK_EDIT_CONTRACT_VERSION,
  type BeginTimelineMultiTrackEditRequest,
  type MultiTrackClipChange,
  type MultiTrackDeleteRange,
  type MultiTrackDescriptor,
  type MultiTrackEditOperation,
  type MultiTrackTimelineClip,
  type TimelineMultiTrackCommitResult,
  type TimelineMultiTrackConflict,
  type TimelineMultiTrackEditConfiguration,
  type TimelineMultiTrackEditEventType,
  type TimelineMultiTrackEditListener,
  type TimelineMultiTrackEditSession,
  type TimelineMultiTrackEditSnapshot,
  type TimelineMultiTrackPreview,
  type TimelineMultiTrackSnapResolver,
} from "../contracts/multi-track-edit-contracts";
import { MultiTrackCollisionModel } from "./multi-track-collision-model";
import { MultiTrackLinkModel } from "./multi-track-link-model";
import { MultiTrackPreviewModel } from "./multi-track-preview-model";

type Config=Required<Omit<TimelineMultiTrackEditConfiguration,"timelineEndFrame">>&{readonly timelineEndFrame:number|null};
const freezeStrings=(items:readonly string[])=>Object.freeze([...new Set(items)].sort());
const freezeConflicts=(items:readonly TimelineMultiTrackConflict[])=>Object.freeze(items.map(i=>Object.freeze({...i})));
const validOperations:readonly MultiTrackEditOperation[]=Object.freeze(["move","ripple-move","ripple-insert","ripple-delete","linked-trim-start","linked-trim-end"]);

export class TimelineMultiTrackEditRuntime {
  private configuration:Config; private version=0; private status:TimelineMultiTrackEditSnapshot["status"]="idle";
  private tracks:readonly MultiTrackDescriptor[]=Object.freeze([]); private clips:readonly MultiTrackTimelineClip[]=Object.freeze([]);
  private session:TimelineMultiTrackEditSession|null=null; private preview:TimelineMultiTrackPreview|null=null; private lastCommit:TimelineMultiTrackCommitResult|null=null;
  private linkGroups:TimelineMultiTrackEditSnapshot["linkGroups"]=Object.freeze([]); private syncRelations:TimelineMultiTrackEditSnapshot["syncRelations"]=Object.freeze([]); private conflicts:readonly TimelineMultiTrackConflict[]=Object.freeze([]);
  private snapResolver:TimelineMultiTrackSnapResolver|null=null; private readonly listeners=new Set<TimelineMultiTrackEditListener>();
  constructor(configuration:TimelineMultiTrackEditConfiguration){this.configuration=this.normalizeConfig(configuration);}
  configure(configuration:Partial<TimelineMultiTrackEditConfiguration>):TimelineMultiTrackEditSnapshot{this.assertUsable();const next=this.normalizeConfig({...this.configuration,...configuration});if(JSON.stringify(next)===JSON.stringify(this.configuration))return this.getSnapshot();this.configuration=next;return this.emit("configured");}
  setSnapResolver(resolver:TimelineMultiTrackSnapResolver):TimelineMultiTrackEditSnapshot{this.assertUsable();if(this.snapResolver===resolver)return this.getSnapshot();this.snapResolver=resolver;return this.emit("snap_resolver_set");}
  clearSnapResolver():TimelineMultiTrackEditSnapshot{this.assertUsable();if(!this.snapResolver)return this.getSnapshot();this.snapResolver=null;return this.emit("snap_resolver_cleared");}
  beginEdit(request:BeginTimelineMultiTrackEditRequest):TimelineMultiTrackEditSnapshot{
    this.assertUsable();if(this.session)return this.getSnapshot();
    this.tracks=Object.freeze(request.tracks.map(t=>Object.freeze({...t})));this.clips=Object.freeze(request.clips.map(c=>Object.freeze({...c})));
    const issues=this.validateBegin(request);const anchor=this.clips.find(c=>c.clipId===(request.anchorClipId??request.selectedClipIds[0]));
    const links=MultiTrackLinkModel.build(this.tracks,this.clips,anchor?.clipId);this.linkGroups=links.linkGroups;this.syncRelations=links.syncRelations;
    const selected=freezeStrings(request.selectedClipIds);const affected=this.planAffected(request,selected,anchor??null);const affectedTracks=freezeStrings(affected.map(id=>this.clips.find(c=>c.clipId===id)?.trackId).filter((v):v is string=>Boolean(v)));
    if(affected.length===0)issues.push(this.issue("empty-affected-set","No clips are affected by this operation"));
    const pivot=this.normalizeFrame(request.pivotFrame??anchor?.timelineStartFrame??0);
    if(anchor)this.session=Object.freeze({sessionId:String(request.sessionId),operation:request.operation,anchorClipId:anchor.clipId,selectedClipIds:selected,affectedClipIds:affected,affectedTrackIds:affectedTracks,pivotFrame:pivot,startedAtVersion:this.version});
    this.conflicts=freezeConflicts(issues);this.preview=null;this.lastCommit=null;this.status=issues.some(i=>i.blocking)?"blocked":"editing";return this.emit(this.status==="blocked"?"edit_blocked":"edit_started");
  }
  previewFrames(deltaFrames:number):TimelineMultiTrackEditSnapshot{return this.calculate(deltaFrames,false);}
  previewTime(deltaSeconds:number):TimelineMultiTrackEditSnapshot{return this.previewFrames(deltaSeconds*this.configuration.framesPerSecond);}
  previewWithSnap(deltaFrames:number):TimelineMultiTrackEditSnapshot{return this.calculate(deltaFrames,true);}
  previewRippleInsert(deltaFrames:number):TimelineMultiTrackEditSnapshot{return this.calculate(Math.abs(deltaFrames),true,"ripple-insert");}
  previewRippleDelete(range:MultiTrackDeleteRange):TimelineMultiTrackEditSnapshot{this.assertSession();if(!Number.isFinite(range.startFrame)||!Number.isFinite(range.endFrame)||range.endFrame<=range.startFrame)throw new Error("Invalid delete range");return this.calculate(-(Math.round(range.endFrame)-Math.round(range.startFrame)),false,"ripple-delete",range);}
  commitEdit():TimelineMultiTrackEditSnapshot{this.assertUsable();if(!this.session)throw new Error("TimelineMultiTrackEditRuntime has no active session");if(!this.preview||this.preview.blocked)throw new Error("TimelineMultiTrackEditRuntime is blocked or has no preview");this.lastCommit=Object.freeze({sessionId:this.session.sessionId,operation:this.session.operation,committed:true,requestedDeltaFrames:this.preview.requestedDeltaFrames,resolvedDeltaFrames:this.preview.resolvedDeltaFrames,affectedClipIds:freezeStrings(this.preview.affectedClipIds),affectedTrackIds:freezeStrings(this.preview.affectedTrackIds),changes:Object.freeze(this.preview.changes.map(c=>Object.freeze({...c,original:Object.freeze({...c.original}),preview:Object.freeze({...c.preview})}))),conflicts:freezeConflicts(this.preview.conflicts)});this.status="committed";return this.emit("edit_committed");}
  cancelEdit():TimelineMultiTrackEditSnapshot{this.assertUsable();if(!this.session)return this.getSnapshot();this.status="cancelled";this.preview=null;this.lastCommit=null;this.conflicts=Object.freeze([]);const s=this.emit("edit_cancelled");this.session=null;return s;}
  subscribe(listener:TimelineMultiTrackEditListener):()=>void{this.assertUsable();this.listeners.add(listener);return()=>this.listeners.delete(listener);}
  getSnapshot():TimelineMultiTrackEditSnapshot{return Object.freeze({contractVersion:TIMELINE_MULTI_TRACK_EDIT_CONTRACT_VERSION,version:this.version,status:this.status,configured:true,session:this.session?Object.freeze({...this.session,selectedClipIds:freezeStrings(this.session.selectedClipIds),affectedClipIds:freezeStrings(this.session.affectedClipIds),affectedTrackIds:freezeStrings(this.session.affectedTrackIds)}):null,preview:this.preview,lastCommit:this.lastCommit,linkGroups:this.linkGroups,syncRelations:this.syncRelations,conflicts:freezeConflicts(this.conflicts)});}
  snapshot():TimelineMultiTrackEditSnapshot{return this.getSnapshot();}
  reset():TimelineMultiTrackEditSnapshot{this.assertUsable();if(this.status==="idle"&&!this.session&&!this.preview&&!this.lastCommit)return this.getSnapshot();this.status="idle";this.session=null;this.preview=null;this.lastCommit=null;this.conflicts=Object.freeze([]);return this.emit("reset");}
  dispose():TimelineMultiTrackEditSnapshot{if(this.status==="disposed")return this.getSnapshot();this.status="disposed";const s=this.emit("disposed");this.listeners.clear();return s;}

  private calculate(deltaInput:number,useSnap:boolean,operationOverride?:MultiTrackEditOperation,deleteRange?:MultiTrackDeleteRange):TimelineMultiTrackEditSnapshot{
    this.assertSession();if(!Number.isFinite(deltaInput)){this.conflicts=freezeConflicts([this.issue("invalid-delta","Delta must be finite")]);this.status="blocked";return this.emit("edit_blocked");}
    const requested=Math.round(deltaInput),session=this.session!,operation=operationOverride??session.operation,anchor=this.clips.find(c=>c.clipId===session.anchorClipId)!;
    let resolved=requested,snapped=false,targetId:string|null=null,targetFrame:number|null=null;
    if(useSnap&&this.configuration.magneticSnapEnabled&&this.snapResolver){const r=this.snapResolver.resolveMultiTrackDelta({operation,anchorClip:anchor,pivotFrame:session.pivotFrame,requestedDeltaFrames:requested,affectedClipIds:session.affectedClipIds,excludedOwnerIds:freezeStrings([...session.selectedClipIds,...session.affectedClipIds])});resolved=Math.round(r.resolvedDeltaFrames);snapped=r.snapped;targetId=r.targetId;targetFrame=r.targetFrame;}
    const bounds=this.deltaBounds(session.affectedClipIds);const before=resolved;if(this.configuration.clampPreviewToTimelineBounds)resolved=Math.max(bounds.min,Math.min(bounds.max,resolved));
    const issues:TimelineMultiTrackConflict[]=[];if(!this.configuration.clampPreviewToTimelineBounds&&(resolved<bounds.min||resolved>bounds.max))issues.push(this.issue(resolved<bounds.min?"timeline-underflow":"timeline-overflow","Preview exceeds timeline bounds"));
    const changes:MultiTrackClipChange[]=[];const previewMap=new Map<string,ReturnType<typeof MultiTrackCollisionModel.position>>();
    for(const clip of this.clips){if(!session.affectedClipIds.includes(clip.clipId))continue;let kind:MultiTrackClipChange["kind"]="moved";
      if(operation==="ripple-move"||operation==="ripple-insert"||operation==="ripple-delete")kind="ripple-shifted";else if(operation==="linked-trim-start")kind="trimmed-start";else if(operation==="linked-trim-end")kind="trimmed-end";
      if(operation==="ripple-delete"&&deleteRange&&clip.timelineStartFrame<deleteRange.endFrame&&clip.timelineEndFrame>deleteRange.startFrame){issues.push(this.issue("pivot-intersects-clip","Delete range intersects a clip",clip));continue;}
      const built=MultiTrackPreviewModel.change(clip,kind,resolved,this.configuration.minimumClipDurationFrames);changes.push(built.change);issues.push(...built.conflicts);previewMap.set(clip.clipId,built.change.preview);
    }
    const collisions=MultiTrackCollisionModel.detect(this.clips,previewMap,this.configuration.timelineStartFrame,this.configuration.timelineEndFrame);if(this.configuration.blockOnCollision&&collisions.length)issues.push(this.issue("collision-detected","A same-track collision was detected"));
    this.validateSync(previewMap,issues);const sorted=Object.freeze(changes.sort((a,b)=>(this.trackOrder(a.trackId)-this.trackOrder(b.trackId))||a.preview.timelineStartFrame-b.preview.timelineStartFrame||a.clipId.localeCompare(b.clipId)));
    const blocked=issues.some(i=>i.blocking);const preview:TimelineMultiTrackPreview=Object.freeze({operation,requestedDeltaFrames:requested,resolvedDeltaFrames:resolved,pivotFrame:session.pivotFrame,previewPivotFrame:session.pivotFrame+resolved,affectedClipIds:session.affectedClipIds,affectedTrackIds:session.affectedTrackIds,changes:sorted,collisions,conflicts:freezeConflicts(issues),snapped,snapTargetId:targetId,snapTargetFrame:targetFrame,clamped:before!==resolved,blocked});
    if(this.preview&&JSON.stringify(this.preview)===JSON.stringify(preview))return this.getSnapshot();this.preview=preview;this.conflicts=preview.conflicts;this.status=blocked?"blocked":"previewing";return this.emit(blocked?"edit_blocked":snapped?"snap_applied":collisions.length?"collision_detected":"preview_updated");
  }
  private validateBegin(request:BeginTimelineMultiTrackEditRequest):TimelineMultiTrackConflict[]{const out:TimelineMultiTrackConflict[]=[];if(!request.sessionId)out.push(this.issue("missing-session-id","Session ID is required"));if(!validOperations.includes(request.operation))out.push(this.issue("invalid-operation","Operation is invalid"));if(request.selectedClipIds.length===0)out.push(this.issue("missing-selection","Selection is required"));const trackIds=new Set<string>();for(const t of request.tracks){if(trackIds.has(t.trackId))out.push(this.issue("duplicate-track-id","Duplicate track ID",undefined,t));trackIds.add(t.trackId);if(!Number.isFinite(t.order))out.push(this.issue("invalid-track-order","Track order must be finite",undefined,t));}const clipIds=new Set<string>();for(const c of request.clips){if(clipIds.has(c.clipId))out.push(this.issue("duplicate-clip-id","Duplicate clip ID",c));clipIds.add(c.clipId);if(!trackIds.has(c.trackId))out.push(this.issue("unknown-track","Clip references an unknown track",c));if(!(c.timelineEndFrame>c.timelineStartFrame))out.push(this.issue("invalid-timeline-range","Clip timeline range is invalid",c));if(c.sourceStartFrame!=null&&(c.sourceEndFrame==null||c.sourceDurationFrames==null||c.sourceStartFrame<0||c.sourceEndFrame<=c.sourceStartFrame||c.sourceEndFrame>c.sourceDurationFrames))out.push(this.issue("invalid-source-range","Clip source range is invalid",c));}
    for(const id of request.selectedClipIds)if(!clipIds.has(id))out.push(this.issue("unknown-selected-clip","Selected clip does not exist",{clipId:id,trackId:""}));const anchorId=request.anchorClipId??request.selectedClipIds[0];if(!anchorId)out.push(this.issue("missing-anchor-clip","Anchor clip is required"));else if(!clipIds.has(anchorId))out.push(this.issue("unknown-anchor-clip","Anchor clip does not exist"));return out;}
  private planAffected(request:BeginTimelineMultiTrackEditRequest,selected:readonly string[],anchor:MultiTrackTimelineClip|null):readonly string[]{const ids=new Set(selected);const include=request.includeLinkedClips??this.configuration.includeLinkedClipsByDefault;if(include){const groups=new Set(this.clips.filter(c=>ids.has(c.clipId)&&c.linkGroupId).map(c=>c.linkGroupId));for(const c of this.clips)if(c.linkGroupId&&groups.has(c.linkGroupId))ids.add(c.clipId);}const pivot=this.normalizeFrame(request.pivotFrame??anchor?.timelineStartFrame??0);if(request.operation.startsWith("ripple")){const allowed=request.affectedTrackIds?new Set(request.affectedTrackIds):new Set(this.tracks.filter(t=>(t.rippleEnabled??true)&&this.configuration.includeRippleEnabledTracksByDefault).map(t=>t.trackId));for(const c of this.clips)if(allowed.has(c.trackId)&&c.timelineStartFrame>=pivot)ids.add(c.clipId);}for(const id of [...ids]){const c=this.clips.find(x=>x.clipId===id),t=c?this.tracks.find(x=>x.trackId===c.trackId):undefined;if((c?.locked&&this.configuration.blockOnLockedClip)||(t?.locked&&this.configuration.blockOnLockedTrack))ids.delete(id);}return freezeStrings([...ids]);}
  private validateSync(preview:ReadonlyMap<string,ReturnType<typeof MultiTrackCollisionModel.position>>,issues:TimelineMultiTrackConflict[]):void{if(!this.configuration.preserveSyncOffsets)return;for(const relation of this.syncRelations){const a=preview.get(relation.anchorClipId)??this.clips.find(c=>c.clipId===relation.anchorClipId);const b=preview.get(relation.linkedClipId)??this.clips.find(c=>c.clipId===relation.linkedClipId);if(a&&b&&b.timelineStartFrame-a.timelineStartFrame!==relation.offsetFrames)issues.push(this.issue("sync-offset-violation","Linked clip sync offset changed"));}}
  private deltaBounds(ids:readonly string[]):{min:number;max:number}{let min=-Infinity,max=Infinity;for(const id of ids){const c=this.clips.find(x=>x.clipId===id);if(!c)continue;min=Math.max(min,this.configuration.timelineStartFrame-c.timelineStartFrame);if(this.configuration.timelineEndFrame!==null)max=Math.min(max,this.configuration.timelineEndFrame-c.timelineEndFrame);}return {min:Number.isFinite(min)?min:-Number.MAX_SAFE_INTEGER,max:Number.isFinite(max)?max:Number.MAX_SAFE_INTEGER};}
  private normalizeConfig(c:TimelineMultiTrackEditConfiguration):Config{if(!Number.isFinite(c.framesPerSecond)||c.framesPerSecond<=0)throw new Error("framesPerSecond must be greater than zero");return Object.freeze({framesPerSecond:c.framesPerSecond,timelineStartFrame:Math.round(c.timelineStartFrame??0),timelineEndFrame:c.timelineEndFrame==null?null:Math.round(c.timelineEndFrame),minimumClipDurationFrames:Math.max(1,Math.round(c.minimumClipDurationFrames??1)),preserveLinkGroups:c.preserveLinkGroups??true,preserveSyncOffsets:c.preserveSyncOffsets??true,includeLinkedClipsByDefault:c.includeLinkedClipsByDefault??true,includeRippleEnabledTracksByDefault:c.includeRippleEnabledTracksByDefault??true,blockOnLockedTrack:c.blockOnLockedTrack??true,blockOnLockedClip:c.blockOnLockedClip??true,blockOnCollision:c.blockOnCollision??true,clampPreviewToTimelineBounds:c.clampPreviewToTimelineBounds??true,magneticSnapEnabled:c.magneticSnapEnabled??true});}
  private issue(code:TimelineMultiTrackConflict["code"],message:string,clip?:Pick<MultiTrackTimelineClip,"clipId"|"trackId">,track?:Pick<MultiTrackDescriptor,"trackId">):TimelineMultiTrackConflict{return Object.freeze({code,message,clipId:clip?.clipId??null,trackId:clip?.trackId??track?.trackId??null,blocking:true});}
  private trackOrder(id:string):number{return this.tracks.find(t=>t.trackId===id)?.order??999999;}
  private normalizeFrame(v:number):number{return Number.isFinite(v)?Math.round(v):0;}
  private emit(type:TimelineMultiTrackEditEventType):TimelineMultiTrackEditSnapshot{this.version++;const s=this.getSnapshot();for(const l of this.listeners)l({type,snapshot:s});return s;}
  private assertSession():void{this.assertUsable();if(!this.session)throw new Error("TimelineMultiTrackEditRuntime has no active session");}
  private assertUsable():void{if(this.status==="disposed")throw new Error("TimelineMultiTrackEditRuntime is disposed");}
}
export const createTimelineMultiTrackEditRuntime=(configuration:TimelineMultiTrackEditConfiguration)=>new TimelineMultiTrackEditRuntime(configuration);
