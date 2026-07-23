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

const playbackRoot = path.resolve(__dirname, "../src/features/playback");
const runtimePath = path.join(playbackRoot, "runtime", "playhead-runtime.ts");
const coordinatePath = path.join(playbackRoot, "runtime", "playhead-coordinate-model.ts");
const source = fs.readFileSync(runtimePath, "utf8") + fs.readFileSync(coordinatePath, "utf8");
const api = {
  ...require(path.join(playbackRoot, "contracts", "index.ts")),
  ...require(path.join(playbackRoot, "runtime", "index.ts")),
  ...require(path.join(playbackRoot, "adapters", "index.ts")),
};

function main() {
  const configuration = { duration: 10, fps: 30, pixelsPerSecond: 100, viewportWidth: 400, scrollOffset: 0, initialTime: 1 };
  const inputCopy = JSON.stringify(configuration);
  const seeks = [];
  const transitions = [];
  const runtime = api.createPlayheadRuntime(configuration, { now: () => "2026-07-21T10:00:00.000Z", requestSeek: (time) => seeks.push(time) });
  const initial = runtime.getSnapshot();
  runtime.subscribe((state, previous, event) => transitions.push(`${previous.stateRevision}->${state.stateRevision}:${event.type}`));
  const ready = runtime.ready();
  const movedTime = runtime.moveToTime(2.5);
  const movedFrame = runtime.moveToFrame(90);
  const movedPixel = runtime.moveToPixel(250);
  const zoomed = runtime.setZoom(200);
  const scrolled = runtime.setScrollOffset(300);
  const viewport = runtime.setViewport(500);
  const boundedLow = runtime.moveToTime(-5);
  const boundedHigh = runtime.moveToTime(99);
  runtime.moveToTime(2);
  const dragStarted = runtime.beginDrag();
  const dragPreview = runtime.dragToPixel(500);
  const ignoredSync = runtime.syncFromPlayback({ currentTime: 1 });
  const dragEnded = runtime.endDrag();
  const seekCountAfterEnd = seeks.length;
  runtime.syncFromPlayback({ currentTime: dragEnded.timeSeconds });
  const seekCountAfterSync = seeks.length;
  runtime.moveToTime(4);
  runtime.beginDrag();
  runtime.dragToPixel(800);
  const cancelled = runtime.cancelDrag();
  const synced = runtime.syncFromPlayback({ currentTime: 6, currentFrame: 180 });
  const isolated = runtime.getSnapshot(); isolated.timeSeconds = 999;
  const snapshotIsolated = runtime.getSnapshot().timeSeconds !== 999;
  const reset = runtime.reset();
  runtime.dispose();
  let disposedBlocked = false; try { runtime.moveToTime(1); } catch { disposedBlocked = true; }

  const checks = {
    contract_version_valid: api.PLAYHEAD_RUNTIME_CONTRACT_VERSION === "16.8.7.2" && initial.contractVersion === "16.8.7.2",
    initial_state_valid: initial.status === "idle" && initial.timeSeconds === 1 && initial.frame === 30 && initial.timelinePixel === 100,
    ready_state_valid: ready.status === "ready" && !ready.isDragging,
    time_to_frame_valid: api.timeToFrame(2.5, 30, 10) === 75,
    frame_to_time_valid: api.frameToTime(90, 30, 10) === 3,
    time_to_pixel_valid: api.timeToTimelinePixel(2.5, 10, 100) === 250,
    pixel_to_time_valid: api.viewportPixelToTime(250, 10, 100, 0) === 2.5,
    viewport_offset_valid: movedPixel.timeSeconds === 2.5 && scrolled.viewportPixel === zoomed.timelinePixel - 300,
    zoom_update_valid: zoomed.timeSeconds === movedPixel.timeSeconds && zoomed.timelinePixel === movedPixel.timeSeconds * 200,
    scroll_update_valid: scrolled.timeSeconds === zoomed.timeSeconds && scrolled.scrollOffset === 300,
    move_to_time_valid: movedTime.timeSeconds === 2.5 && movedTime.frame === 75,
    move_to_frame_valid: movedFrame.timeSeconds === 3 && movedFrame.frame === 90,
    move_to_pixel_valid: movedPixel.timeSeconds === 2.5,
    duration_bounds_enforced: boundedLow.timeSeconds === 0 && boundedHigh.timeSeconds === 10,
    frame_bounds_enforced: api.coordinateFromFrame(9999, 10, 30, 100, 0).frame === 300,
    pixel_bounds_enforced: api.viewportPixelToTime(9999, 10, 100, 0) === 10,
    drag_begin_valid: dragStarted.status === "dragging" && dragStarted.isDragging,
    drag_preview_valid: dragPreview.status === "dragging" && dragPreview.timeSeconds === 4,
    drag_end_valid: dragEnded.status === "synced" && !dragEnded.isDragging,
    drag_cancel_restores_position: cancelled.timeSeconds === 4 && !cancelled.isDragging,
    playback_sync_valid: synced.timeSeconds === 6 && synced.frame === 180,
    playback_sync_ignored_while_dragging: ignoredSync.timeSeconds === dragPreview.timeSeconds && ignoredSync.isDragging,
    seek_emitted_once: seekCountAfterEnd === 1,
    no_feedback_loop: seekCountAfterSync === 1,
    snapshots_isolated: snapshotIsolated,
    inputs_unchanged: JSON.stringify(configuration) === inputCopy,
    transitions_emitted_once: new Set(transitions).size === transitions.length,
    reset_valid: reset.status === "idle" && reset.timeSeconds === 1 && reset.pixelsPerSecond === 100 && reset.scrollOffset === 0,
    disposed_blocked: disposedBlocked,
    no_react_dependency: !source.includes('from "react"') && !source.includes("from 'react'"),
    no_dom_dependency: !source.includes("document.") && !source.includes("window.") && !source.includes("HTMLVideoElement"),
    no_backend_or_timeline_mutation: !source.includes("fetch(") && !source.includes("axios") && !source.includes("moveClip(") && !source.includes("trimClip") && !source.includes("timeline.tracks"),
    viewport_update_valid: viewport.viewportWidth === 500 && viewport.timeSeconds === scrolled.timeSeconds,
  };
  console.log("=== Playhead Runtime ===");
  for (const [name, value] of Object.entries(checks)) { console.log(`${name}: ${value}`); assert.equal(value, true, `${name} failed`); }
  console.log("\nDONE: Playhead runtime test completed.");
}
main();
