/* eslint-disable @typescript-eslint/no-require-imports */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const ts = require("typescript");

require.extensions[".ts"] = function compile(module, filename) {
  const source = fs.readFileSync(filename, "utf8");
  const output = ts.transpileModule(source, {
    fileName: filename,
    compilerOptions: {
      target: ts.ScriptTarget.ES2022,
      module: ts.ModuleKind.CommonJS,
      moduleResolution: ts.ModuleResolutionKind.NodeJs,
      esModuleInterop: true,
    },
  });
  module._compile(output.outputText, filename);
};

const playbackRoot = path.resolve(__dirname, "../src/features/playback");
const runtimePath = path.join(playbackRoot, "runtime", "playback-session-runtime.ts");
const source = fs.readFileSync(runtimePath, "utf8");
const { PLAYBACK_SESSION_CONTRACT_VERSION } = require(path.join(playbackRoot, "contracts", "index.ts"));
const { createPlaybackSessionRuntime } = require(path.join(playbackRoot, "runtime", "index.ts"));

function main() {
  const configuration = { duration: 10, fps: 30, initialTime: 1 };
  const inputCopy = JSON.stringify(configuration);
  const transitions = [];
  const runtime = createPlaybackSessionRuntime(configuration, {
    now: () => "2026-07-21T09:00:00.000Z",
  });
  const initial = runtime.getSnapshot();
  const unsubscribe = runtime.subscribe((state, previous, event) => {
    transitions.push(`${previous.stateRevision}->${state.stateRevision}:${event.type}`);
  });

  const ready = runtime.ready();
  const playing = runtime.play();
  const advanced = runtime.advance(1);
  const paused = runtime.pause();
  const seeked = runtime.seek(5.25);
  const speed = runtime.setSpeed(2);
  const loop = runtime.setLoop(true);
  const steppedForward = runtime.stepForward();
  const steppedBackward = runtime.stepBackward(2);
  const boundedLow = runtime.seek(-100);
  const boundedHigh = runtime.seek(100);

  runtime.setLoop(false);
  runtime.seek(9.8);
  runtime.play();
  const completed = runtime.advance(1);

  runtime.setLoop(true);
  runtime.play();
  runtime.seek(9.8);
  runtime.play();
  const looped = runtime.advance(1);

  const isolated = runtime.getSnapshot();
  isolated.currentTime = 999;
  const snapshotIsolated = runtime.getSnapshot().currentTime !== 999;

  const stopped = runtime.stop();
  const reset = runtime.reset();
  unsubscribe();
  runtime.dispose();

  let disposedBlocked = false;
  try { runtime.play(); } catch { disposedBlocked = true; }

  const checks = {
    contract_version_valid:
      PLAYBACK_SESSION_CONTRACT_VERSION === "16.8.7.1" &&
      initial.contractVersion === "16.8.7.1",
    initial_state_valid:
      initial.status === "idle" && initial.currentTime === 1 &&
      initial.currentFrame === 30 && initial.playing === false,
    ready_state_valid: ready.status === "ready" && ready.playing === false,
    play_transition_valid: playing.status === "playing" && playing.playing === true,
    pause_transition_valid: paused.status === "paused" && paused.playing === false,
    stop_transition_valid: stopped.status === "stopped" && stopped.currentTime === 0,
    seek_transition_valid: seeked.status === "seeking" && seeked.currentFrame === 158,
    speed_transition_valid: speed.speed === 2,
    loop_transition_valid: loop.loop === true,
    frame_step_valid:
      steppedForward.currentFrame === 159 && steppedBackward.currentFrame === 157,
    duration_bounds_enforced: boundedLow.currentTime === 0 && boundedHigh.currentTime === 10,
    advance_uses_speed: advanced.currentTime === 2,
    completion_valid:
      completed.status === "completed" && completed.currentTime === 10 && !completed.playing,
    loop_completion_valid:
      looped.status === "playing" && looped.currentTime > 0 && looped.currentTime < 10,
    snapshots_isolated: snapshotIsolated,
    inputs_unchanged: JSON.stringify(configuration) === inputCopy,
    transitions_emitted_once:
      transitions.length === 22 && new Set(transitions).size === transitions.length,
    reset_valid:
      reset.status === "idle" && reset.currentTime === 0 && reset.speed === 1 && !reset.loop,
    disposed_blocked: disposedBlocked,
    no_react_dependency: !source.includes("react"),
    no_api_or_timeline_mutation:
      !source.includes("fetch(") && !source.includes("axios") &&
      !source.includes("timeline.tracks") && !source.includes("moveClip(") &&
      !source.includes("trimClip") && !source.includes("HTMLVideoElement"),
  };

  console.log("=== Playback Session Runtime ===");
  for (const [name, value] of Object.entries(checks)) {
    console.log(`${name}: ${value}`);
    assert.equal(value, true, `${name} failed`);
  }
  console.log("\nDONE: Playback session runtime test completed.");
}
main();
