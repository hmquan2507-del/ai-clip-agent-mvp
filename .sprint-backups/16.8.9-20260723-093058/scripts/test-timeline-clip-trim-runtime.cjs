/* eslint-disable @typescript-eslint/no-require-imports */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),ts=require('typescript');
require.extensions['.ts']=(m,f)=>{const s=fs.readFileSync(f,'utf8');const o=ts.transpileModule(s,{fileName:f,compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.CommonJS,moduleResolution:ts.ModuleResolutionKind.NodeJs,esModuleInterop:true}});m._compile(o.outputText,f)};
const api=require(path.resolve(__dirname,'../src/features/playback/index.ts'));
const clip={clipId:'clip-a',trackId:'video-1',timelineStartFrame:100,timelineEndFrame:200,sourceStartFrame:20,sourceEndFrame:120,sourceDurationFrames:180};
const input=JSON.parse(JSON.stringify(clip));
const cfg={framesPerSecond:30,minimumDurationFrames:10,snapThresholdFrames:3,snapTargets:[{id:'playhead',frame:150,type:'playhead'},{id:'marker',frame:190,type:'marker'},{id:'zero',frame:0,type:'timeline-zero'}]};
const r=api.createTimelineClipTrimRuntime(cfg); const initial=r.getSnapshot(); const events=[]; r.subscribe(e=>events.push(e.type));
const beginStart=r.beginTrim({clip,edge:'start'}); const duplicateCount=events.length; r.beginTrim({clip,edge:'start'}); const duplicateBegin=events.length===duplicateCount;
const startPreview=r.previewTrimFrames(10,false); const timePreview=r.previewTrimTime(1,false);
const snappedStart=r.previewTrimFrames(48,true); const previewEvents=events.length; r.previewTrimFrames(48,true); const noDuplicatePreview=events.length===previewEvents;
const committed=r.commitTrim(); const commitCount=events.filter(x=>x==='trim_committed').length;
const rEnd=api.createTimelineClipTrimRuntime(cfg); const endBegin=rEnd.beginTrim({clip,edge:'end'}); const endPreview=rEnd.previewTrimFrames(-10,false); const snappedEnd=rEnd.previewTrimFrames(-8,true);
const rCancel=api.createTimelineClipTrimRuntime(cfg); rCancel.beginTrim({clip,edge:'end'}); rCancel.previewTrimFrames(20,false); const cancelled=rCancel.cancelTrim();
const rMin=api.createTimelineClipTrimRuntime(cfg); rMin.beginTrim({clip,edge:'start'}); const minBound=rMin.previewTrimFrames(1000,false);
const rSourceStart=api.createTimelineClipTrimRuntime(cfg); rSourceStart.beginTrim({clip,edge:'start'}); const sourceStartBound=rSourceStart.previewTrimFrames(-1000,false);
const rSourceEnd=api.createTimelineClipTrimRuntime(cfg); rSourceEnd.beginTrim({clip,edge:'end'}); const sourceEndBound=rSourceEnd.previewTrimFrames(1000,false);
const zeroClip={...clip,timelineStartFrame:5,sourceStartFrame:40,sourceEndFrame:140}; const rZero=api.createTimelineClipTrimRuntime(cfg); rZero.beginTrim({clip:zeroClip,edge:'start'}); const zeroBound=rZero.previewTrimFrames(-100,false);
const snap=r.getSnapshot(); let immutable=false; try{snap.preview.timelineStartFrame=0}catch{immutable=true}
const source=fs.readFileSync(path.resolve(__dirname,'../src/features/playback/runtime/timeline-clip-trim-runtime.ts'),'utf8');
const reset=r.reset(); r.dispose(); let disposed=false; try{r.beginTrim({clip,edge:'start'})}catch{disposed=true}
const checks={
 contract_version_valid:api.TIMELINE_CLIP_TRIM_CONTRACT_VERSION==='16.8.7.8'&&initial.contractVersion==='16.8.7.8',
 initial_state_valid:initial.status==='idle'&&initial.preview===null,
 configuration_valid:cfg.minimumDurationFrames===10,
 begin_start_trim_valid:beginStart.status==='trimming'&&beginStart.edge==='start',
 begin_end_trim_valid:endBegin.status==='trimming'&&endBegin.edge==='end',
 duplicate_begin_prevented:duplicateBegin,
 origin_capture_valid:beginStart.origin.timelineStartFrame===100&&beginStart.origin.sourceStartFrame===20,
 start_trim_preview_valid:startPreview.preview.timelineStartFrame===110&&startPreview.preview.timelineEndFrame===200,
 end_trim_preview_valid:endPreview.preview.timelineEndFrame===190&&endPreview.preview.sourceEndFrame===110,
 frame_trim_valid:startPreview.deltaFrames===10,
 time_trim_valid:timePreview.deltaFrames===30&&timePreview.deltaTimeSeconds===1,
 timeline_source_mapping_valid:startPreview.preview.timelineStartFrame-startPreview.origin.timelineStartFrame===startPreview.preview.sourceStartFrame-startPreview.origin.sourceStartFrame,
 minimum_duration_enforced:minBound.preview.durationFrames===10&&minBound.preview.timelineStartFrame===190,
 source_start_bound_enforced:sourceStartBound.preview.sourceStartFrame===0&&sourceStartBound.deltaFrames===-20,
 source_end_bound_enforced:sourceEndBound.preview.sourceEndFrame===180&&sourceEndBound.deltaFrames===60,
 timeline_zero_bound_enforced:zeroBound.preview.timelineStartFrame===0&&zeroBound.deltaFrames===-5,
 snap_valid:snappedStart.snappedFrame===150&&snappedStart.snappedTargetId==='playhead'&&snappedStart.preview.timelineStartFrame===150,
 snap_threshold_valid:snappedEnd.snappedFrame===190&&snappedEnd.preview.timelineEndFrame===190,
 duplicate_preview_prevented:noDuplicatePreview,
 commit_valid:committed.status==='committed'&&committed.commitResult&&committed.commitResult.deltaFrames===50,
 commit_emitted_once:commitCount===1,
 cancel_valid:cancelled.status==='cancelled',
 cancel_restores_origin:cancelled.preview.timelineEndFrame===200&&cancelled.deltaFrames===0,
 immutable_snapshot_valid:immutable||Object.isFrozen(snap.preview),
 inputs_unchanged:JSON.stringify(input)===JSON.stringify(clip),
 transitions_emitted_once:events.filter(x=>x==='trim_started').length===1&&events.filter(x=>x==='preview_updated').length===3,
 reset_valid:reset.status==='idle'&&reset.preview===null&&reset.origin===null,
 disposed_blocked:disposed,
 no_react_dependency:!source.includes('react'),
 core_runtime_has_no_dom_dependency:!source.includes('HTMLElement')&&!source.includes('PointerEvent')&&!source.includes('document.'),
 no_backend_or_timeline_mutation:!source.includes('fetch(')&&!source.includes('axios')&&!source.includes('trimClip(')&&!source.includes('updateTimeline(')
};
console.log('=== Timeline Resize & Trim Runtime ===');for(const[k,v]of Object.entries(checks)){console.log(`${k}: ${Boolean(v)}`);assert.equal(Boolean(v),true,`${k} failed`)}console.log('\nDONE: Timeline resize & trim runtime test completed.');
