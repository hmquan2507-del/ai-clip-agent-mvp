/* eslint-disable @typescript-eslint/no-require-imports */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),ts=require('typescript');
require.extensions['.ts']=(m,f)=>{const s=fs.readFileSync(f,'utf8');const o=ts.transpileModule(s,{fileName:f,compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.CommonJS,moduleResolution:ts.ModuleResolutionKind.NodeJs,esModuleInterop:true}});m._compile(o.outputText,f)};
const api=require(path.resolve(__dirname,'../src/features/playback/index.ts'));
const clips=[
 {clipId:'a',trackId:'v1',startFrame:100,endFrame:130},
 {clipId:'b',trackId:'v1',startFrame:140,endFrame:170},
];
const input=JSON.parse(JSON.stringify(clips));
const r=api.createTimelineClipMoveRuntime({framesPerSecond:30,durationFrames:400,snapThresholdFrames:4,snapTargets:[150,220]});
const initial=r.getSnapshot(); const events=[]; r.subscribe(e=>events.push(e.type));
const begin=r.beginMove({activeClipId:'a',clips}); const duplicateBefore=events.length; r.beginMove({activeClipId:'a',clips}); const duplicateBegin=events.length===duplicateBefore;
const preview=r.previewMoveFrames(20,false); const spacing=preview.previewPositions[1].previewStartFrame-preview.previewPositions[0].previewStartFrame;
const timePreview=r.previewMoveTime(1,false); const snapped=r.previewMoveFrames(48,true); const snapStableEvents=events.length; r.previewMoveFrames(48,true); const noDuplicatePreview=events.length===snapStableEvents;
const committed=r.commitMove(); const commitEvents=events.filter(x=>x==='move_committed').length;
const r2=api.createTimelineClipMoveRuntime({framesPerSecond:30,durationFrames:400,snapThresholdFrames:3,snapTargets:[150]}); r2.beginMove({activeClipId:'a',clips}); r2.previewMoveFrames(25,false); const cancelled=r2.cancelMove();
const snap=r.getSnapshot(); let immutable=false; try{snap.previewPositions.push({})}catch{immutable=true}
const source=fs.readFileSync(path.resolve(__dirname,'../src/features/playback/runtime/timeline-clip-move-runtime.ts'),'utf8');
const reset=r.reset(); r.dispose(); let disposed=false; try{r.beginMove({activeClipId:'a',clips})}catch{disposed=true}
const checks={
 contract_version_valid:api.TIMELINE_CLIP_MOVE_CONTRACT_VERSION==='16.8.7.7'&&initial.contractVersion==='16.8.7.7',
 initial_state_valid:initial.status==='idle',
 begin_move_valid:begin.status==='moving'&&begin.selectedClipIds.join(',')==='a,b',
 duplicate_begin_prevented:duplicateBegin,
 origin_capture_valid:begin.previewPositions[0].originStartFrame===100&&begin.previewPositions[1].originStartFrame===140,
 preview_move_valid:preview.previewPositions[0].previewStartFrame===120,
 frame_move_valid:preview.deltaFrames===20,
 time_move_valid:timePreview.deltaFrames===30&&timePreview.deltaTimeSeconds===1,
 multi_clip_move_valid:preview.previewPositions.length===2,
 relative_spacing_preserved:spacing===40,
 snap_valid:snapped.snappedFrame===150&&snapped.previewPositions[0].previewStartFrame===150,
 snap_threshold_valid:snapped.deltaFrames===50,
 duplicate_preview_prevented:noDuplicatePreview,
 commit_valid:committed.status==='committed'&&committed.commitResult&&committed.commitResult.deltaFrames===50,
 commit_emitted_once:commitEvents===1,
 cancel_valid:cancelled.status==='cancelled',
 preview_restored:cancelled.previewPositions[0].previewStartFrame===100&&cancelled.deltaFrames===0,
 immutable_snapshot_valid:immutable||snap.previewPositions.length===2,
 inputs_unchanged:JSON.stringify(input)===JSON.stringify(clips),
 transitions_emitted_once:events.filter(x=>x==='move_started').length===1&&events.filter(x=>x==='preview_updated').length===3,
 reset_valid:reset.status==='idle'&&reset.previewPositions.length===0,
 disposed_blocked:disposed,
 no_react_dependency:!source.includes('react'),
 core_runtime_has_no_dom_dependency:!source.includes('HTMLElement')&&!source.includes('PointerEvent')&&!source.includes('document.'),
 no_backend_or_timeline_mutation:!source.includes('fetch(')&&!source.includes('axios')&&!source.includes('moveClip(')&&!source.includes('updateTimeline(')
};
console.log('=== Timeline Clip Move Runtime ===');for(const[k,v]of Object.entries(checks)){console.log(`${k}: ${Boolean(v)}`);assert.equal(Boolean(v),true,`${k} failed`)}console.log('\nDONE: Timeline clip move runtime test completed.');
