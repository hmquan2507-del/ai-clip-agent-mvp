import {
 TIMELINE_MAGNETIC_SNAP_CONTRACT_VERSION,
 type PreviewMagneticMoveRequest,type PreviewMagneticTrimRequest,type ResolveTimelineSnapRequest,
 type TimelineMagneticPreview,type TimelineMagneticSnapConfiguration,type TimelineMagneticSnapEventType,
 type TimelineMagneticSnapListener,type TimelineMagneticSnapSnapshot,type TimelineSnapCandidate,
 type TimelineSnapGuide,type TimelineSnapResult,type TimelineSnapSource,type TimelineSnapTarget,type TimelineSnapTargetType,
} from "../contracts/magnetic-snap-contracts";
import { compareSnapCandidates, DEFAULT_TIMELINE_SNAP_PRIORITIES, normalizeSnapTarget } from "./snap-candidate-model";
import { createSnapGuide } from "./snap-guide-model";

type ResolvedConfiguration={framesPerSecond:number;enabled:boolean;magneticEnabled:boolean;thresholdFrames:number;thresholdPixels:number;pixelsPerSecond:number;zoom:number;timelineStartFrame:number;timelineEndFrame:number|null;preferSameTrack:boolean;sameTrackPriorityBoost:number;targetTypePriorities:Readonly<Record<TimelineSnapTargetType,number>>};
const freeze=<T>(v:T):T=>{if(v&&typeof v==="object"&&!Object.isFrozen(v)){Object.freeze(v);for(const x of Object.values(v as Record<string,unknown>))freeze(x)}return v};
const finite=(v:number,fallback:number)=>Number.isFinite(v)?v:fallback;
const resolveConfig=(c:TimelineMagneticSnapConfiguration):ResolvedConfiguration=>freeze({
 framesPerSecond:Math.max(0.0001,finite(c.framesPerSecond,30)),enabled:c.enabled!==false,magneticEnabled:c.magneticEnabled!==false,
 thresholdFrames:Math.max(0,finite(c.thresholdFrames??3,3)),thresholdPixels:Math.max(0,finite(c.thresholdPixels??8,8)),
 pixelsPerSecond:Math.max(0,finite(c.pixelsPerSecond??100,100)),zoom:Math.max(0,finite(c.zoom??1,1)),
 timelineStartFrame:Math.round(finite(c.timelineStartFrame??0,0)),timelineEndFrame:Number.isFinite(c.timelineEndFrame as number)?Math.round(c.timelineEndFrame as number):null,
 preferSameTrack:c.preferSameTrack!==false,sameTrackPriorityBoost:finite(c.sameTrackPriorityBoost??25,25),
 targetTypePriorities:freeze({...DEFAULT_TIMELINE_SNAP_PRIORITIES,...(c.targetTypePriorities??{})}),
});
const emptyResult=(s:TimelineSnapSource):TimelineSnapResult=>freeze({snapped:false,originalFrame:s.frame,resolvedFrame:s.frame,deltaFrames:0,sourceId:s.sourceId,sourceEdge:s.edge,targetId:null,targetType:null,targetFrame:null,candidateCount:0,guide:null});
const same=(a:unknown,b:unknown)=>JSON.stringify(a)===JSON.stringify(b);
export function createTimelineMagneticSnapEngine(initial?:TimelineMagneticSnapConfiguration){
 let disposed=false,version=0,config:ResolvedConfiguration|null=initial?resolveConfig(initial):null,targets:readonly TimelineSnapTarget[]=freeze([]),lastResult:TimelineSnapResult|null=null,guides:readonly TimelineSnapGuide[]=freeze([]),lastPreviewKey="";
 const listeners=new Set<TimelineMagneticSnapListener>();
 const ensure=()=>{if(disposed)throw new Error("Timeline magnetic snap engine is disposed")};
 const snapshot=():TimelineMagneticSnapSnapshot=>freeze({contractVersion:TIMELINE_MAGNETIC_SNAP_CONTRACT_VERSION,version,status:disposed?"disposed":guides.length?"previewing":config?"ready":"idle",configured:!!config,enabled:config?.enabled??false,magneticEnabled:config?.magneticEnabled??false,targetCount:targets.length,targets:freeze(targets.map(x=>freeze({...x}))),lastResult:lastResult?freeze({...lastResult}):null,activeGuides:freeze(guides.map(x=>freeze({...x,sourceIds:freeze([...x.sourceIds])})))});
 const emit=(type:TimelineMagneticSnapEventType)=>{version++;const s=snapshot();for(const l of listeners)l(freeze({type,snapshot:s}))};
 const normalize=(input:readonly TimelineSnapTarget[])=>{const c=config??resolveConfig({framesPerSecond:30});const m=new Map<string,TimelineSnapTarget>();for(const t of input){const n=normalizeSnapTarget(t,c.timelineStartFrame,c.timelineEndFrame);if(n&&!m.has(n.targetId))m.set(n.targetId,n)}return freeze([...m.values()].sort((a,b)=>a.frame-b.frame||a.targetId.localeCompare(b.targetId)))};
 const configure=(c:TimelineMagneticSnapConfiguration)=>{ensure();const next=resolveConfig(c);if(!same(config,next)){config=next;targets=normalize(targets);emit("configured")}return snapshot()};
 const setTargets=(x:readonly TimelineSnapTarget[])=>{ensure();const n=normalize(x);if(!same(targets,n)){targets=n;emit("targets_replaced")}return snapshot()};
 const addTargets=(x:readonly TimelineSnapTarget[])=>{ensure();const n=normalize([...targets,...x]);if(!same(targets,n)){targets=n;emit("targets_added")}return snapshot()};
 const removeTargets=(ids:readonly string[])=>{ensure();const s=new Set(ids);const n=freeze(targets.filter(x=>!s.has(x.targetId)));if(n.length!==targets.length){targets=n;emit("targets_removed")}return snapshot()};
 const clearTargets=()=>{ensure();if(targets.length){targets=freeze([]);guides=freeze([]);emit("targets_cleared")}return snapshot()};
 const candidates=(source:TimelineSnapSource,request:ResolveTimelineSnapRequest):{items:TimelineSnapCandidate[];map:Map<string,TimelineSnapTarget>}=>{
  const c=config??resolveConfig({framesPerSecond:30});if(!c.enabled)return {items:[],map:new Map()};const list=normalize(request.targets??targets),exT=new Set(request.excludeTargetIds??[]),exO=new Set(request.excludeOwnerIds??[]),allowed=request.allowedTargetTypes?new Set(request.allowedTargetTypes):null,map=new Map<string,TimelineSnapTarget>(),items:TimelineSnapCandidate[]=[];
  const fpp=c.pixelsPerSecond>0&&c.zoom>0?c.framesPerSecond/(c.pixelsPerSecond*c.zoom):null;
  for(const t of list){if(t.enabled===false||exT.has(t.targetId)||(t.ownerId&&exO.has(t.ownerId))||(allowed&&!allowed.has(t.type)))continue;const d=t.frame-source.frame,abs=Math.abs(d),px=fpp&&fpp>0?abs/fpp:null;if(!(abs<=c.thresholdFrames||(px!==null&&px<=c.thresholdPixels)))continue;const sameTrack=!!(source.trackId&&t.trackId&&source.trackId===t.trackId);const base=t.priority??c.targetTypePriorities[t.type];const effective=base+(c.preferSameTrack&&sameTrack?c.sameTrackPriorityBoost:0);items.push(freeze({sourceId:source.sourceId,sourceEdge:source.edge,sourceFrame:source.frame,targetId:t.targetId,targetType:t.type,targetFrame:t.frame,deltaFrames:d,absoluteDistanceFrames:abs,distancePixels:px,basePriority:base,effectivePriority:effective,sameTrack}));map.set(t.targetId,t)}
  items.sort(compareSnapCandidates);return {items,map};
 };
 const resolveInternal=(request:ResolveTimelineSnapRequest,emitEvent:boolean):TimelineSnapResult=>{ensure();const source=freeze({...request.source,frame:Math.round(request.source.frame)});const c=candidates(source,request);let result:TimelineSnapResult;if(!c.items.length)result=emptyResult(source);else{const best=c.items[0],target=c.map.get(best.targetId)!;const guide=createSnapGuide(best,target,[source.sourceId]);result=freeze({snapped:true,originalFrame:source.frame,resolvedFrame:best.targetFrame,deltaFrames:best.deltaFrames,sourceId:source.sourceId,sourceEdge:source.edge,targetId:best.targetId,targetType:best.targetType,targetFrame:best.targetFrame,candidateCount:c.items.length,guide})}if(!same(lastResult,result)){lastResult=result;guides=result.guide?freeze([result.guide]):freeze([]);if(emitEvent)emit("snap_resolved")}return result};
 const resolveSnap=(r:ResolveTimelineSnapRequest)=>resolveInternal(r,true);
 const resolveSnapFrames=resolveSnap;
 const resolveSnapTime=(r:ResolveTimelineSnapRequest & {readonly timeSeconds:number})=>resolveInternal({...r,source:{...r.source,frame:Math.round(r.timeSeconds*(config?.framesPerSecond??30))}},true);
 const previewMagneticMove=(r:PreviewMagneticMoveRequest):TimelineMagneticPreview=>{ensure();if(!r.sources.length)throw new Error("At least one source is required");const proposed=r.sources.map(s=>freeze({...s,frame:Math.round(s.frame+r.proposedDeltaFrames)}));const results=proposed.map(s=>resolveInternal({source:s,excludeTargetIds:r.excludeTargetIds,excludeOwnerIds:r.excludeOwnerIds,allowedTargetTypes:r.allowedTargetTypes},false));const snapped=results.filter(x=>x.snapped).sort((a,b)=>{const ca=targets.find(t=>t.targetId===a.targetId),cb=targets.find(t=>t.targetId===b.targetId);const pa=ca?.priority??config?.targetTypePriorities[a.targetType!]??0,pb=cb?.priority??config?.targetTypePriorities[b.targetType!]??0;return pb-pa||Math.abs(a.deltaFrames)-Math.abs(b.deltaFrames)||a.resolvedFrame-b.resolvedFrame||(a.targetId??"").localeCompare(b.targetId??"")});const primary=snapped[0]??emptyResult(proposed[0]);const correction=primary.snapped?primary.deltaFrames:0;const resolved=freeze(proposed.map(s=>s.frame+correction));const guide=primary.guide?freeze([{...primary.guide,sourceIds:freeze(r.sources.map(s=>s.sourceId))}]):freeze([]);const preview=freeze({originalFrames:freeze(r.sources.map(s=>s.frame)),resolvedFrames:resolved,primaryResult:primary,guides:guide});const key=JSON.stringify(preview);if(key!==lastPreviewKey){lastPreviewKey=key;lastResult=primary;guides=guide;emit("magnetic_preview_updated")}return preview};
 const previewMagneticTrim=(r:PreviewMagneticTrimRequest):TimelineMagneticPreview=>{const src=freeze({...r.source,frame:Math.round(r.proposedFrame)});const result=resolveInternal({source:src,excludeTargetIds:r.excludeTargetIds,excludeOwnerIds:r.excludeOwnerIds,allowedTargetTypes:r.allowedTargetTypes},false);const preview=freeze({originalFrames:freeze([r.source.frame]),resolvedFrames:freeze([result.resolvedFrame]),primaryResult:result,guides:result.guide?freeze([result.guide]):freeze([])});const key=JSON.stringify(preview);if(key!==lastPreviewKey){lastPreviewKey=key;lastResult=result;guides=preview.guides;emit("magnetic_preview_updated")}return preview};
 const clearPreview=()=>{ensure();if(lastResult||guides.length){lastResult=null;guides=freeze([]);lastPreviewKey="";emit("preview_cleared")}return snapshot()};
 const reset=()=>{ensure();config=null;targets=freeze([]);lastResult=null;guides=freeze([]);lastPreviewKey="";emit("reset");return snapshot()};
 const dispose=()=>{if(!disposed){disposed=true;listeners.clear();version++;}return snapshot()};
 return {configure,setTargets,addTargets,removeTargets,clearTargets,resolveSnap,resolveSnapFrames,resolveSnapTime,previewMagneticMove,previewMagneticTrim,clearPreview,getSnapshot:snapshot,snapshot,subscribe:(l:TimelineMagneticSnapListener)=>{ensure();listeners.add(l);return()=>listeners.delete(l)},reset,dispose};
}
