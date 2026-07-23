import {
  TIMELINE_ROLL_EDIT_CONTRACT_VERSION,
  type BeginTimelineRollEditRequest,
  type RollClipPosition,
  type RollTimelineClip,
  type TimelineRollCommitResult,
  type TimelineRollConflict,
  type TimelineRollEditConfiguration,
  type TimelineRollEditEventType,
  type TimelineRollEditListener,
  type TimelineRollEditSession,
  type TimelineRollEditSnapshot,
  type TimelineRollSnapResolver,
} from "../contracts/roll-edit-contracts";
import { RollPreviewModel, type NormalizedRollConfiguration, type RollSnapProjection } from "./roll-preview-model";

const freezeConflicts=(items:readonly TimelineRollConflict[])=>Object.freeze(items.map(i=>Object.freeze({...i})));
const freezePositions=(items:readonly RollClipPosition[]):readonly [RollClipPosition,RollClipPosition]=>Object.freeze(items.map(i=>Object.freeze({...i}))) as readonly [RollClipPosition,RollClipPosition];

export class TimelineRollEditRuntime {
  private configuration:NormalizedRollConfiguration;
  private version=0;
  private status:TimelineRollEditSnapshot["status"]="idle";
  private session:TimelineRollEditSession|null=null;
  private leftClip:RollTimelineClip|null=null;
  private rightClip:RollTimelineClip|null=null;
  private preview:TimelineRollEditSnapshot["preview"]=null;
  private lastCommit:TimelineRollCommitResult|null=null;
  private conflicts:readonly TimelineRollConflict[]=Object.freeze([]);
  private snapResolver:TimelineRollSnapResolver|null=null;
  private readonly listeners=new Set<TimelineRollEditListener>();

  constructor(configuration:TimelineRollEditConfiguration){this.configuration=this.normalizeConfiguration(configuration);}
  configure(configuration:Partial<TimelineRollEditConfiguration>):TimelineRollEditSnapshot{this.assertUsable();const next=this.normalizeConfiguration({...this.configuration,...configuration});if(JSON.stringify(next)===JSON.stringify(this.configuration))return this.getSnapshot();this.configuration=next;return this.emit("configured");}
  setSnapResolver(resolver:TimelineRollSnapResolver):TimelineRollEditSnapshot{this.assertUsable();if(this.snapResolver===resolver)return this.getSnapshot();this.snapResolver=resolver;return this.emit("snap_resolver_set");}
  clearSnapResolver():TimelineRollEditSnapshot{this.assertUsable();if(!this.snapResolver)return this.getSnapshot();this.snapResolver=null;return this.emit("snap_resolver_cleared");}

  beginRollEdit(request:BeginTimelineRollEditRequest):TimelineRollEditSnapshot{
    this.assertUsable();if(this.session)return this.getSnapshot();
    const left=request.leftClip?RollPreviewModel.normalizeClip(request.leftClip):null;
    const right=request.rightClip?RollPreviewModel.normalizeClip(request.rightClip):null;
    const issues=RollPreviewModel.beginConflicts(left,right,this.configuration);
    this.leftClip=left;this.rightClip=right;this.preview=null;this.lastCommit=null;this.conflicts=freezeConflicts(issues);
    if(left&&right)this.session=Object.freeze({sessionId:String(request.sessionId),leftClipId:left.clipId,rightClipId:right.clipId,trackId:left.trackId,originalCutFrame:left.timelineEndFrame,startedAtVersion:this.version});
    this.status=issues.some(i=>i.blocking)?"blocked":"editing";
    return this.emit(this.status==="blocked"?"roll_blocked":"roll_started");
  }

  previewRollFrames(deltaFrames:number):TimelineRollEditSnapshot{return this.calculate(deltaFrames);}
  previewRollTime(deltaSeconds:number):TimelineRollEditSnapshot{return this.previewRollFrames(deltaSeconds*this.configuration.framesPerSecond);}
  previewRollCutFrame(cutFrame:number):TimelineRollEditSnapshot{this.assertSession();return this.previewRollFrames(cutFrame-this.session!.originalCutFrame);}
  previewRollWithSnap(deltaFrames:number):TimelineRollEditSnapshot{
    this.assertSession();if(!this.leftClip||!this.rightClip)return this.getSnapshot();
    const normalized=Number.isFinite(deltaFrames)?Math.round(deltaFrames):deltaFrames;
    let snap:RollSnapProjection|undefined;
    if(this.configuration.magneticSnapEnabled&&this.snapResolver){
      snap=this.snapResolver.resolveRollCut({originalCutFrame:this.session!.originalCutFrame,proposedCutFrame:this.session!.originalCutFrame+normalized,leftClip:this.leftClip,rightClip:this.rightClip,excludedOwnerIds:Object.freeze([this.leftClip.clipId,this.rightClip.clipId])});
    }
    return this.calculate(deltaFrames,snap);
  }

  commitRollEdit():TimelineRollEditSnapshot{this.assertUsable();if(!this.session)throw new Error("TimelineRollEditRuntime has no active session");if(this.status==="blocked")throw new Error("TimelineRollEditRuntime is blocked");if(!this.preview)throw new Error("TimelineRollEditRuntime has no preview");this.lastCommit=Object.freeze({sessionId:this.session.sessionId,committed:true,originalCutFrame:this.preview.originalCutFrame,committedCutFrame:this.preview.previewCutFrame,requestedDeltaFrames:this.preview.requestedDeltaFrames,resolvedDeltaFrames:this.preview.resolvedDeltaFrames,positions:freezePositions([this.preview.leftPreview,this.preview.rightPreview]),conflicts:freezeConflicts(this.preview.conflicts)});this.status="committed";return this.emit("roll_committed");}
  cancelRollEdit():TimelineRollEditSnapshot{this.assertUsable();if(!this.session)return this.getSnapshot();this.status="cancelled";this.preview=null;this.conflicts=Object.freeze([]);this.lastCommit=null;const snapshot=this.emit("roll_cancelled");this.session=null;this.leftClip=null;this.rightClip=null;return snapshot;}
  subscribe(listener:TimelineRollEditListener):()=>void{this.assertUsable();this.listeners.add(listener);return()=>this.listeners.delete(listener);}
  getSnapshot():TimelineRollEditSnapshot{return Object.freeze({contractVersion:TIMELINE_ROLL_EDIT_CONTRACT_VERSION,version:this.version,status:this.status,configured:true,session:this.session?Object.freeze({...this.session}):null,preview:this.preview,lastCommit:this.lastCommit,conflicts:freezeConflicts(this.conflicts)});}
  snapshot():TimelineRollEditSnapshot{return this.getSnapshot();}
  reset():TimelineRollEditSnapshot{this.assertUsable();if(this.status==="idle"&&!this.session&&!this.preview&&!this.lastCommit&&this.conflicts.length===0)return this.getSnapshot();this.status="idle";this.session=null;this.leftClip=null;this.rightClip=null;this.preview=null;this.lastCommit=null;this.conflicts=Object.freeze([]);return this.emit("reset");}
  dispose():TimelineRollEditSnapshot{if(this.status==="disposed")return this.getSnapshot();this.status="disposed";const snapshot=this.emit("disposed");this.listeners.clear();return snapshot;}

  private calculate(deltaFrames:number,snap?:RollSnapProjection):TimelineRollEditSnapshot{this.assertSession();if(!this.leftClip||!this.rightClip)return this.getSnapshot();const preview=RollPreviewModel.calculate(this.leftClip,this.rightClip,deltaFrames,this.configuration,snap);if(this.preview&&JSON.stringify(this.preview)===JSON.stringify(preview))return this.getSnapshot();this.preview=preview;this.conflicts=freezeConflicts(preview.conflicts);this.status=preview.blocked?"blocked":"previewing";return this.emit(preview.blocked?"roll_blocked":snap?.snapped?"roll_snap_applied":"roll_preview_updated");}
  private normalizeConfiguration(configuration:TimelineRollEditConfiguration):NormalizedRollConfiguration{if(!Number.isFinite(configuration.framesPerSecond)||configuration.framesPerSecond<=0)throw new Error("framesPerSecond must be greater than zero");const minimumClipDurationFrames=Math.max(1,Math.round(configuration.minimumClipDurationFrames??1));const timelineStartFrame=Math.round(configuration.timelineStartFrame??0);const timelineEndFrame=configuration.timelineEndFrame==null?null:Math.round(configuration.timelineEndFrame);if(timelineEndFrame!==null&&timelineEndFrame<=timelineStartFrame)throw new Error("timelineEndFrame must be greater than timelineStartFrame");return Object.freeze({framesPerSecond:configuration.framesPerSecond,minimumClipDurationFrames,timelineStartFrame,timelineEndFrame,requireContiguousClips:configuration.requireContiguousClips??true,blockOnLockedClip:configuration.blockOnLockedClip??true,clampPreviewToValidRange:configuration.clampPreviewToValidRange??true,magneticSnapEnabled:configuration.magneticSnapEnabled??true});}
  private emit(type:TimelineRollEditEventType):TimelineRollEditSnapshot{this.version+=1;const snapshot=this.getSnapshot();for(const listener of this.listeners)listener({type,snapshot});return snapshot;}
  private assertSession():void{this.assertUsable();if(!this.session)throw new Error("TimelineRollEditRuntime has no active session");if(this.status==="blocked"&&!this.preview)throw new Error("TimelineRollEditRuntime is blocked");}
  private assertUsable():void{if(this.status==="disposed")throw new Error("TimelineRollEditRuntime is disposed");}
}
export const createTimelineRollEditRuntime=(configuration:TimelineRollEditConfiguration):TimelineRollEditRuntime=>new TimelineRollEditRuntime(configuration);
