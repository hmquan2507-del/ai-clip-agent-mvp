/* eslint-disable @typescript-eslint/no-require-imports */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),ts=require('typescript');
require.extensions['.ts']=(m,f)=>{const s=fs.readFileSync(f,'utf8');const o=ts.transpileModule(s,{fileName:f,compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.CommonJS,moduleResolution:ts.ModuleResolutionKind.NodeJs,esModuleInterop:true}});m._compile(o.outputText,f)};
const api=require(path.resolve(__dirname,'../src/features/playback/index.ts'));
const clips=[
 {clipId:'a',trackId:'v1',timelineStartFrame:0,timelineEndFrame:100,sourceStartFrame:0,sourceEndFrame:100},
 {clipId:'b',trackId:'v1',timelineStartFrame:100,timelineEndFrame:200,sourceStartFrame:0,sourceEndFrame:100},
 {clipId:'c',trackId:'v1',timelineStartFrame:200,timelineEndFrame:300,sourceStartFrame:0,sourceEndFrame:100},
 {clipId:'x',trackId:'v2',timelineStartFrame:100,timelineEndFrame:200,sourceStartFrame:0,sourceEndFrame:100},
];
const original=JSON.stringify(clips);
const cfg={framesPerSecond:30,timelineStartFrame:0,timelineEndFrame:1000,affectSameTrackOnly:true,preserveRelativeSpacing:true,blockOnLockedClip:true,preventOverlap:true};
const pos=(snap,id)=>snap.previewPositions.find(p=>p.clipId===id);
const r=api.createTimelineRippleEditRuntime(cfg), initial=r.getSnapshot(), events=[];r.subscribe(e=>events.push(e.type));
const configured=r.configure({timelineEndFrame:900});
const begin=r.beginRippleEdit({clips,operation:'move',anchorClipId:'a'});const n=events.length;r.beginRippleEdit({clips,operation:'move',anchorClipId:'a'});const duplicateBegin=events.length===n;
const move=r.previewRippleFrames(20);const spacingBefore=pos(move,'c').timelineStartFrame-pos(move,'b').timelineStartFrame;const pe=events.length;r.previewRippleFrames(20);const duplicatePreview=events.length===pe;
const time=r.previewRippleTime(1);const committed=r.commitRippleEdit();const commitCount=events.filter(x=>x==='ripple_committed').length;
const rt=api.createTimelineRippleEditRuntime(cfg);const bt=rt.beginRippleEdit({clips,operation:'trim-end',anchorClipId:'a'});const trimEnd=rt.previewRippleFrames(-20);
const rs=api.createTimelineRippleEditRuntime(cfg);const bs=rs.beginRippleEdit({clips,operation:'trim-start',anchorClipId:'a'});const trimStart=rs.previewRippleFrames(10);
const rg=api.createTimelineRippleEditRuntime(cfg);const gap=rg.previewDeleteGap({clips:[clips[0],{...clips[1],timelineStartFrame:140,timelineEndFrame:240},{...clips[2],timelineStartFrame:240,timelineEndFrame:340}],trackId:'v1',gapStartFrame:100,gapEndFrame:140});
const rc=api.createTimelineRippleEditRuntime(cfg);rc.beginRippleEdit({clips,operation:'move',anchorClipId:'a'});rc.previewRippleFrames(15);const cancelled=rc.cancelRippleEdit();
const lockedClips=clips.map(c=>c.clipId==='b'?{...c,locked:true}:c);const rl=api.createTimelineRippleEditRuntime(cfg);rl.beginRippleEdit({clips:lockedClips,operation:'move',anchorClipId:'a'});const locked=rl.previewRippleFrames(10);let blockedCommit=false;try{rl.commitRippleEdit()}catch{blockedCommit=true}
const ru=api.createTimelineRippleEditRuntime(cfg);ru.beginRippleEdit({clips,operation:'move',anchorClipId:'a'});const under=ru.previewRippleFrames(-10);
const ro=api.createTimelineRippleEditRuntime({...cfg,timelineEndFrame:310});ro.beginRippleEdit({clips,operation:'move',anchorClipId:'a'});const overflow=ro.previewRippleFrames(20);
const overlapClips=[clips[0],clips[1],clips[2]];const rov=api.createTimelineRippleEditRuntime(cfg);rov.beginRippleEdit({clips:overlapClips,operation:'trim-start',anchorClipId:'b'});const overlap=rov.previewRippleFrames(-20);
const rm=api.createTimelineRippleEditRuntime(cfg);const missing=rm.beginRippleEdit({clips,operation:'move',anchorClipId:'missing'});
const snap=r.getSnapshot();let immutable=false;try{snap.previewPositions[0].timelineStartFrame=999}catch{immutable=true}
const source=fs.readFileSync(path.resolve(__dirname,'../src/features/playback/runtime/timeline-ripple-edit-runtime.ts'),'utf8');
const reset=r.reset();r.dispose();let disposed=false;try{r.beginRippleEdit({clips,operation:'move',anchorClipId:'a'})}catch{disposed=true}
const checks={
 contract_version_valid:api.TIMELINE_RIPPLE_EDIT_CONTRACT_VERSION==='16.8.7.9'&&initial.contractVersion==='16.8.7.9',
 initial_state_valid:initial.status==='idle'&&initial.previewPositions.length===0,
 configuration_valid:configured.status==='idle'&&configured.version===1,
 begin_move_ripple_valid:begin.status==='editing'&&begin.operation==='move',
 begin_trim_start_ripple_valid:bs.status==='editing'&&bs.operation==='trim-start',
 begin_trim_end_ripple_valid:bt.status==='editing'&&bt.operation==='trim-end',
 duplicate_begin_prevented:duplicateBegin,
 anchor_capture_valid:begin.anchorClipId==='a'&&begin.trackId==='v1',
 same_track_affected_only:move.affectedClipIds.includes('b')&&move.affectedClipIds.includes('c')&&!move.affectedClipIds.includes('x'),
 downstream_clips_detected:move.affectedClipIds.join(',')==='b,c',
 upstream_clips_unchanged:pos(trimStart,'a').timelineEndFrame===100,
 move_ripple_preview_valid:pos(move,'a').timelineStartFrame===20&&pos(move,'b').timelineStartFrame===120,
 trim_start_ripple_preview_valid:pos(trimStart,'a').timelineStartFrame===10&&pos(trimStart,'a').sourceStartFrame===10,
 trim_end_ripple_preview_valid:pos(trimEnd,'a').timelineEndFrame===80&&pos(trimEnd,'b').timelineStartFrame===80,
 frame_preview_valid:move.deltaFrames===20,
 time_preview_valid:time.deltaFrames===30,
 relative_spacing_preserved:spacingBefore===100,
 track_order_preserved:pos(move,'b').timelineStartFrame<pos(move,'c').timelineStartFrame,
 delete_gap_preview_valid:gap.operation==='delete-gap'&&gap.deltaFrames===-40,
 delete_gap_closes_space:pos(gap,'b').timelineStartFrame===100&&pos(gap,'c').timelineStartFrame===200,
 locked_clip_conflict_detected:locked.status==='blocked'&&locked.conflicts.some(c=>c.type==='locked-clip'),
 timeline_underflow_detected:under.status==='blocked'&&under.conflicts.some(c=>c.type==='timeline-underflow'),
 timeline_end_bound_enforced:overflow.status==='blocked'&&overflow.conflicts.some(c=>c.type==='timeline-overflow'),
 overlap_conflict_detected:overlap.status==='blocked'&&overlap.conflicts.some(c=>c.type==='overlap'),
 missing_anchor_blocked:missing.status==='blocked'&&missing.conflicts.some(c=>c.type==='missing-anchor'),
 blocked_commit_rejected:blockedCommit,
 duplicate_preview_prevented:duplicatePreview,
 commit_valid:committed.status==='committed'&&committed.commitResult&&committed.commitResult.deltaFrames===30,
 commit_emitted_once:commitCount===1,
 cancel_valid:cancelled.status==='cancelled',
 cancel_restores_origin:pos(cancelled,'a').timelineStartFrame===0&&cancelled.deltaFrames===0,
 immutable_snapshot_valid:immutable||Object.isFrozen(snap.previewPositions[0]),
 inputs_unchanged:JSON.stringify(clips)===original,
 transitions_emitted_once:events.filter(x=>x==='ripple_started').length===1&&events.filter(x=>x==='ripple_committed').length===1,
 reset_valid:reset.status==='idle'&&reset.previewPositions.length===0,
 disposed_blocked:disposed,
 no_react_dependency:!source.includes('react'),
 core_runtime_has_no_dom_dependency:!source.includes('HTMLElement')&&!source.includes('PointerEvent')&&!source.includes('document.'),
 no_backend_or_timeline_mutation:!source.includes('fetch(')&&!source.includes('axios')&&!source.includes('updateTimeline(')&&!source.includes('mutateTimeline(')
};
console.log('=== Timeline Ripple Editing Runtime ===');for(const[k,v]of Object.entries(checks)){console.log(`${k}: ${Boolean(v)}`);assert.equal(Boolean(v),true,`${k} failed`)}console.log('\nDONE: Timeline ripple editing runtime test completed.');
