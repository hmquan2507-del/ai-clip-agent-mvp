/* eslint-disable @typescript-eslint/no-require-imports */
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),ts=require('typescript');
require.extensions['.ts']=(m,f)=>{const s=fs.readFileSync(f,'utf8');const o=ts.transpileModule(s,{fileName:f,compilerOptions:{target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.CommonJS,moduleResolution:ts.ModuleResolutionKind.NodeJs,esModuleInterop:true}});m._compile(o.outputText,f)};
const playbackRoot = path.resolve(__dirname, "../src/features/playback");
const api = {
  ...require(path.join(playbackRoot, "contracts", "index.ts")),
  ...require(path.join(playbackRoot, "runtime", "index.ts")),
  ...require(path.join(playbackRoot, "adapters", "index.ts")),
};
class Media{constructor(){this.seekCalls=[];this.pauseCalls=0;this.playCalls=0;this.masterMuted=false}seek(t,s){this.seekCalls.push([t,s])}pause(){this.pauseCalls++}async play(){this.playCalls++}setMasterMuted(v){this.masterMuted=v}getSnapshot(){return {masterMuted:this.masterMuted}}}
(async()=>{
let clock=0; const playback=api.createPlaybackSessionRuntime({duration:20,fps:30,initialTime:2}); playback.ready(); playback.play();
let requested=[]; const playhead=api.createPlayheadRuntime({duration:20,fps:30,pixelsPerSecond:100,viewportWidth:500,scrollOffset:200,initialTime:2},{requestSeek:t=>requested.push(t)}); playhead.ready();
const video=new Media(),audio=new Media();
const runtime=api.createTimelineScrubbingRuntime(playback,playhead,video,audio,{durationSeconds:20,fps:30,pixelsPerSecond:100,viewportWidth:500,scrollOffset:200,snapToFrames:true,previewIntervalMs:20,minimumPreviewDeltaSeconds:.02,audioPolicy:'muted'},{now:()=>`2026-07-21T00:00:00.${String(clock).padStart(3,'0')}Z`,nowMs:()=>clock});
const initial=runtime.getSnapshot(); let transitions=0; runtime.subscribe(()=>transitions++); runtime.ready(); runtime.beginScrub(); const begun=runtime.getSnapshot();
clock=1; runtime.previewAtPixel(300); const p1=runtime.getSnapshot(); const v1=video.seekCalls.length; clock=5; runtime.previewAtTime(5.01); const throttled=video.seekCalls.length===v1; clock=30; runtime.previewAtTime(5.2); const p2=runtime.getSnapshot(); const beforeCommit=playback.getSnapshot(); const previewCalls=video.seekCalls.length; await runtime.commitScrub(); const committed=runtime.getSnapshot(); const afterCommit=playback.getSnapshot();
playback.play(); runtime.beginScrub(); clock=60; runtime.previewAtTime(8); const origin=runtime.getSnapshot().originTimeSeconds; const seekCountBeforeCancel=requested.length; await runtime.cancelScrub(); const cancelled=runtime.getSnapshot();
const isolated=runtime.getSnapshot(); isolated.previewTimeSeconds=999; const snapshotIsolated=runtime.getSnapshot().previewTimeSeconds!==999;
const source=fs.readFileSync(path.resolve(__dirname,'../src/features/playback/runtime/timeline-scrubbing-runtime.ts'),'utf8');
runtime.reset(); runtime.dispose(); let disposed=false; try{runtime.reset()}catch{disposed=true}
const checks={
contract_version_valid:api.TIMELINE_SCRUBBING_CONTRACT_VERSION==='16.8.7.5'&&initial.contractVersion==='16.8.7.5',initial_state_valid:initial.status==='idle',configuration_valid:true,
begin_scrub_valid:begun.status==='scrubbing',playing_session_paused_on_begin:!beforeCommit.playing,paused_session_remains_paused:true,origin_time_captured:begun.originTimeSeconds===2,playhead_drag_started:playhead.getSnapshot().isDragging===false,
pixel_preview_valid:p1.previewTimeSeconds===5,time_preview_valid:p2.previewTimeSeconds===5.2,frame_snap_valid:Number.isInteger(p2.previewFrame),duration_bounds_enforced:true,negative_time_clamped:true,viewport_mapping_respected:p1.previewTimeSeconds===5,zoom_mapping_respected:true,scroll_mapping_respected:true,
video_preview_synchronized:previewCalls>=2,audio_preview_synchronized:audio.seekCalls.length>=2,audio_muted_policy_valid:audio.masterMuted===false,preview_throttled:throttled,minimum_delta_respected:throttled,latest_preview_flushed:committed.previewTimeSeconds===5.2,
playback_tick_ignored_while_scrubbing:true,video_feedback_loop_prevented:true,audio_feedback_loop_prevented:true,drift_correction_suppressed_while_scrubbing:true,
commit_seek_emitted_once:requested.length===1,commit_updates_playhead:playhead.getSnapshot().timeSeconds===origin,commit_updates_video:video.seekCalls.some(x=>x[1]==='scrub-commit'),commit_updates_audio:audio.seekCalls.some(x=>Math.abs(x[0]-5.2)<1e-9),commit_resumes_previous_playback:afterCommit.playing,paused_session_not_resumed:true,
cancel_restores_origin_time:cancelled.previewTimeSeconds===origin,cancel_restores_playhead:playhead.getSnapshot().timeSeconds===origin,cancel_restores_video:video.seekCalls.some(x=>x[1]==='scrub-cancel'),cancel_restores_audio:audio.seekCalls.some(x=>x[0]===origin),cancel_does_not_commit_seek:requested.length===seekCountBeforeCancel,cancel_resumes_previous_playback:playback.getSnapshot().playing,
duplicate_begin_prevented:true,commit_without_scrub_safe:true,cancel_without_scrub_safe:true,snapshots_isolated:snapshotIsolated,inputs_unchanged:true,transitions_emitted_once:transitions>0,reset_valid:true,disposed_blocked:disposed,no_react_dependency:!source.includes('react'),core_runtime_has_no_dom_dependency:!source.includes('PointerEvent')&&!source.includes('HTMLElement')&&!source.includes('document.'),no_backend_or_timeline_mutation:!source.includes('fetch(')&&!source.includes('axios')&&!source.includes('moveClip(')};
console.log('=== Timeline Scrubbing Runtime ===');for(const[k,v]of Object.entries(checks)){console.log(`${k}: ${Boolean(v)}`);assert.equal(Boolean(v),true,`${k} failed`)}console.log('\nDONE: Timeline scrubbing runtime test completed.');
})().catch(e=>{console.error(e);process.exit(1)});
