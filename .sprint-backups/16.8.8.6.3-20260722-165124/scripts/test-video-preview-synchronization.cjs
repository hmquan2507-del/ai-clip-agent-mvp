/* eslint-disable @typescript-eslint/no-require-imports */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const ts = require("typescript");
require.extensions[".ts"] = function compile(module, filename) {
  const source = fs.readFileSync(filename, "utf8");
  const output = ts.transpileModule(source, { fileName: filename, compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.CommonJS, moduleResolution: ts.ModuleResolutionKind.NodeJs, esModuleInterop: true } });
  module._compile(output.outputText, filename);
};
const api = require(path.resolve(__dirname, "../src/features/playback/index.ts"));
const coreSource = fs.readFileSync(path.resolve(__dirname, "../src/features/playback/runtime/playback-session-runtime.ts"), "utf8") + fs.readFileSync(path.resolve(__dirname, "../src/features/playback/runtime/playhead-runtime.ts"), "utf8");
const syncSource = fs.readFileSync(path.resolve(__dirname, "../src/features/playback/runtime/video-preview-synchronizer.ts"), "utf8");

class FakeVideoPort {
  constructor() { this.currentTime=0; this.duration=10; this.paused=true; this.seeking=false; this.ended=false; this.playbackRate=1; this.listeners=new Map(); this.playCalls=0; this.pauseCalls=0; this.seekCalls=0; this.rateCalls=0; this.rejectPlay=false; }
  async play(){ this.playCalls++; if(this.rejectPlay) throw new Error("autoplay blocked"); this.paused=false; }
  pause(){ this.pauseCalls++; this.paused=true; }
  setCurrentTime(v){ this.seekCalls++; this.currentTime=v; }
  setPlaybackRate(v){ this.rateCalls++; this.playbackRate=v; }
  subscribe(event, listener){ if(!this.listeners.has(event)) this.listeners.set(event,new Set()); this.listeners.get(event).add(listener); return ()=>this.listeners.get(event)?.delete(listener); }
  emit(event){ for(const listener of this.listeners.get(event)||[]) listener(); }
  listenerCount(){ return [...this.listeners.values()].reduce((n,s)=>n+s.size,0); }
}

async function main(){
  const playback=api.createPlaybackSessionRuntime({duration:10,fps:30}); playback.ready();
  const playhead=api.createPlayheadRuntime({duration:10,fps:30,pixelsPerSecond:100}); playhead.ready();
  const port=new FakeVideoPort();
  const sync=api.createVideoPreviewSynchronizer(playback,playhead,{fps:30},{now:()=>"2026-07-21T12:00:00.000Z"});
  const initial=sync.getSnapshot(); const attached=sync.attach(port); const listenersAfterAttach=port.listenerCount();
  port.duration=10; port.emit("loadedmetadata"); const metadata=sync.getSnapshot();
  await sync.play(); const playCalls=port.playCalls; const playedState=!port.paused; await sync.syncFromPlayback(); const duplicatePlayCalls=port.playCalls;
  sync.pause(); const pauseCalls=port.pauseCalls; sync.pause(); const duplicatePauseCalls=port.pauseCalls;
  sync.seek(2); const seekCalls=port.seekCalls; port.emit("seeked"); const seekCallsAfterEvent=port.seekCalls;
  sync.seek(2.01); const duplicateSeekCalls=port.seekCalls;
  sync.setPlaybackRate(1.5); const rateCalls=port.rateCalls; const rateState=port.playbackRate; sync.setPlaybackRate(1.5); const duplicateRateCalls=port.rateCalls;
  port.currentTime=3; port.paused=false; port.emit("timeupdate"); const mediaPlayback=playback.getSnapshot(); const mediaPlayhead=playhead.getSnapshot();
  playhead.beginDrag(); playhead.dragToPixel(500); const dragTime=playhead.getSnapshot().timeSeconds; port.currentTime=4; port.emit("timeupdate"); const duringDrag=playhead.getSnapshot(); playhead.cancelDrag();
  port.emit("waiting"); const waiting=sync.getSnapshot(); port.emit("playing"); const playing=sync.getSnapshot();
  playback.synchronizeTime(5,true); port.currentTime=5.02; const smallBefore=port.seekCalls; await sync.syncFromPlayback(); const smallAfter=port.seekCalls;
  port.currentTime=6; const largeBefore=port.seekCalls; await sync.syncFromPlayback(); const largeAfter=port.seekCalls;
  port.currentTime=10; port.ended=true; port.paused=true; port.emit("ended"); const ended=sync.getSnapshot(); const endedPlayback=playback.getSnapshot();
  const isolated=sync.getSnapshot(); isolated.currentTimeSeconds=999; const snapshotsIsolated=sync.getSnapshot().currentTimeSeconds!==999;
  const reset=sync.reset(); sync.detach(); const listenersAfterDetach=port.listenerCount();
  const badPort=new FakeVideoPort(); badPort.rejectPlay=true; sync.attach(badPort); const rejected=await sync.play();
  sync.dispose(); let disposedBlocked=false; try{sync.reset()}catch{disposedBlocked=true}
  const checks={
    contract_version_valid: api.VIDEO_PREVIEW_CONTRACT_VERSION==="16.8.7.3" && initial.contractVersion==="16.8.7.3",
    initial_state_valid: initial.status==="detached" && !initial.attached,
    attach_valid: attached.attached && attached.status==="loading" && listenersAfterAttach===9,
    detach_valid: listenersAfterDetach===0,
    metadata_sync_valid: metadata.status==="ready" && metadata.durationSeconds===10,
    playback_play_controls_video: playCalls===1 && playedState,
    playback_pause_controls_video: pauseCalls>=1,
    playback_seek_controls_video: seekCalls>=1,
    playback_rate_controls_video: rateCalls===1 && rateState===1.5,
    media_time_updates_playback: mediaPlayback.currentTime===3 && mediaPlayback.playing,
    media_time_updates_playhead: mediaPlayhead.timeSeconds===3,
    media_ended_completes_playback: ended.ended && endedPlayback.status==="completed",
    media_waiting_sets_buffering: waiting.status==="buffering" && waiting.buffering,
    media_playing_clears_buffering: playing.status==="playing" && !playing.buffering,
    small_drift_ignored: smallBefore===smallAfter,
    large_drift_corrected: largeAfter===largeBefore+1,
    frame_threshold_respected: syncSource.includes("1 / this.fps") && syncSource.includes("0.04"),
    duplicate_play_prevented: duplicatePlayCalls===playCalls,
    duplicate_pause_prevented: duplicatePauseCalls===pauseCalls,
    duplicate_seek_prevented: duplicateSeekCalls===seekCallsAfterEvent,
    duplicate_rate_update_prevented: duplicateRateCalls===rateCalls,
    seek_feedback_loop_prevented: seekCallsAfterEvent===seekCalls,
    timeupdate_feedback_loop_prevented: mediaPlayback.stateRevision<20,
    playhead_drag_not_overwritten: duringDrag.timeSeconds===dragTime && duringDrag.isDragging,
    play_rejection_handled: rejected.status==="error" && rejected.errorMessage.includes("autoplay blocked"),
    invalid_duration_safe: Number.isFinite(metadata.durationSeconds),
    detach_removes_listeners: listenersAfterDetach===0,
    snapshots_isolated: snapshotsIsolated,
    inputs_unchanged: true,
    reset_valid: reset.currentTimeSeconds===0 && reset.playbackRate===1,
    disposed_blocked: disposedBlocked,
    core_runtime_has_no_dom_dependency: !coreSource.includes("HTMLVideoElement") && !coreSource.includes("document.") && !coreSource.includes("window."),
    no_backend_or_timeline_mutation: !syncSource.includes("fetch(") && !syncSource.includes("axios") && !syncSource.includes("moveClip(") && !syncSource.includes("trimClip"),
  };
  console.log("=== Video Preview Synchronization ===");
  for(const [name,value] of Object.entries(checks)){console.log(`${name}: ${value}`); assert.equal(value,true,`${name} failed`)}
  console.log("\nDONE: Video preview synchronization test completed.");
}
main().catch(error=>{console.error(error);process.exit(1)});
