/* eslint-disable @typescript-eslint/no-require-imports */

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const ts = require("typescript");

require.extensions[".ts"] = function compileTypeScript(module, filename) {
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

const trimIndexPath = path.resolve(
  __dirname,
  "../src/features/review/trim/index.ts",
);
const runtimePath = path.resolve(
  __dirname,
  "../src/features/review/trim/runtime.ts",
);
const runtimeSource = fs.readFileSync(runtimePath, "utf8");

const {
  REVIEW_TIMELINE_TRIM_RUNTIME_CONTRACT_VERSION,
  createReviewTimelineTrimSessionRuntime,
} = require(trimIndexPath);

const source = {
  clipId: "clip-1",
  trackId: "video-1",
  startTime: 2,
  endTime: 8,
  duration: 6,
  editable: true,
  trackLocked: false,
};
const environment = {
  viewport: {
    left: 100,
    top: 200,
    width: 500,
    height: 100,
    scrollLeft: 0,
    contentWidth: 1000,
  },
  timelineDuration: 20,
  fps: 30,
  minimumDuration: 1,
};
const armInput = {
  productionId: "production-1",
  timelineRevision: 9,
  handle: "start",
  source,
  pointer: {
    clientX: 200,
    clientY: 240,
  },
  environment,
};
const armInputBefore = structuredClone(armInput);

function main() {
  let sequence = 0;
  const transitions = [];
  const runtime = createReviewTimelineTrimSessionRuntime({
    trimThreshold: 4,
    createSessionId: () => `trim-${++sequence}`,
    now: () => "2026-07-19T08:00:00.000Z",
  });

  const initial = runtime.getState();
  const unsubscribe = runtime.subscribe((state, previous) => {
    transitions.push(`${previous.phase}->${state.phase}`);
  });

  const armed = runtime.arm(armInput);
  const belowThreshold = runtime.move({
    pointer: { clientX: 203, clientY: 240 },
  });

  let earlyCommitBlocked = false;
  try {
    runtime.prepareCommit();
  } catch {
    earlyCommitBlocked = true;
  }

  const trimming = runtime.move({
    pointer: { clientX: 250, clientY: 240 },
  });
  const intent = runtime.prepareCommit();
  const committing = runtime.getState();

  if (intent.operation === "trim_clip_start") {
    intent.newStartTime = 999;
  }
  const runtimeIntent = runtime.getState().commitIntent;
  const intentIsolated =
    runtimeIntent?.operation === "trim_clip_start" &&
    runtimeIntent.newStartTime !== 999;

  let secondCommitBlocked = false;
  try {
    runtime.prepareCommit();
  } catch {
    secondCommitBlocked = true;
  }

  const completed = runtime.completeCommit();
  const cancelStart = runtime.arm({
    ...armInput,
    handle: "end",
    timelineRevision: 10,
  });
  runtime.move({
    pointer: { clientX: 550, clientY: 240 },
  });
  const cancelled = runtime.cancel("escape_pressed");

  const isolatedSnapshot = runtime.getState();
  isolatedSnapshot.session.source.clipId = "changed-outside";
  isolatedSnapshot.environment.viewport.left = 999;
  const stateSnapshotIsolated =
    runtime.getState().session.source.clipId === "clip-1" &&
    runtime.getState().environment.viewport.left === 100;

  const invalidRuntime = createReviewTimelineTrimSessionRuntime({
    trimThreshold: 0,
    createSessionId: () => "trim-invalid",
  });
  invalidRuntime.arm({
    ...armInput,
    source: { ...source, trackLocked: true },
  });
  const invalidProjection = invalidRuntime.move({
    pointer: { clientX: 250, clientY: 240 },
  });
  let invalidCommitBlocked = false;
  try {
    invalidRuntime.prepareCommit();
  } catch {
    invalidCommitBlocked = true;
  }

  const failureRuntime = createReviewTimelineTrimSessionRuntime({
    trimThreshold: 0,
    createSessionId: () => "trim-failure",
  });
  failureRuntime.arm(armInput);
  failureRuntime.move({
    pointer: { clientX: 250, clientY: 240 },
  });
  failureRuntime.prepareCommit();
  const failed = failureRuntime.failCommit({
    code: "revision_conflict",
    message: "Revision changed.",
    technicalMessage: "expected 9, received 10",
    isRevisionConflict: true,
    expectedRevision: 9,
    currentRevision: 10,
  });
  const failedSnapshot = failureRuntime.getState();
  failedSnapshot.lastFailure.message = "changed-outside";
  const failureSnapshotIsolated =
    failureRuntime.getState().lastFailure.message ===
    "Revision changed.";

  const resetState = runtime.reset();
  unsubscribe();
  runtime.dispose();

  let disposedBlocked = false;
  try {
    runtime.arm(armInput);
  } catch {
    disposedBlocked = true;
  }

  const checks = {
    contract_version_valid:
      REVIEW_TIMELINE_TRIM_RUNTIME_CONTRACT_VERSION === "16.7.2" &&
      initial.contractVersion === "16.7.2",
    initial_idle:
      initial.phase === "idle" && initial.session === null,
    arm_valid:
      armed.phase === "armed" &&
      armed.session.sessionId === "trim-1" &&
      armed.session.timelineRevision === 9 &&
      armed.session.handle === "start",
    below_threshold_stays_armed:
      belowThreshold.phase === "armed",
    early_commit_blocked: earlyCommitBlocked,
    trim_transition_valid:
      trimming.phase === "trimming" &&
      trimming.pointerDistance >= 4,
    projection_is_preview_only:
      trimming.projection.valid === true &&
      trimming.commitIntent === null &&
      source.startTime === 2,
    commit_intent_valid:
      committing.phase === "committing" &&
      committing.commitIntent.operation === "trim_clip_start" &&
      committing.commitIntent.clipId === "clip-1" &&
      !("expectedRevision" in committing.commitIntent) &&
      !("expected_revision" in committing.commitIntent),
    intent_isolated: intentIsolated,
    exactly_one_commit_prepared: secondCommitBlocked,
    completion_returns_idle:
      completed.phase === "idle" &&
      completed.session === null &&
      completed.lastCommittedIntent.operation === "trim_clip_start",
    cancel_is_read_only:
      cancelStart.session.timelineRevision === 10 &&
      cancelled.phase === "cancelled" &&
      cancelled.cancelReason === "escape_pressed" &&
      cancelled.commitIntent === null &&
      source.endTime === 8,
    invalid_projection_blocked:
      invalidProjection.projection.valid === false &&
      invalidProjection.projection.blockedReason === "track_locked" &&
      invalidCommitBlocked,
    failure_state_valid:
      failed.phase === "failed" &&
      failed.commitIntent === null &&
      failed.failure.isRevisionConflict === true &&
      failed.lastFailure.currentRevision === 10,
    failure_snapshot_isolated: failureSnapshotIsolated,
    state_snapshots_isolated: stateSnapshotIsolated,
    inputs_unchanged:
      JSON.stringify(armInput) === JSON.stringify(armInputBefore),
    transitions_emitted_once:
      transitions.length === 9 &&
      transitions.filter(
        (transition) => transition === "trimming->committing",
      ).length === 1,
    reset_valid:
      resetState.phase === "idle" && resetState.session === null,
    disposed_blocked: disposedBlocked,
    no_api_or_timeline_mutation:
      !runtimeSource.includes("fetch(") &&
      !runtimeSource.includes("trimClipStart(") &&
      !runtimeSource.includes("trimClipEnd(") &&
      !runtimeSource.includes("timeline.tracks") &&
      !runtimeSource.includes("expected_revision"),
  };

  console.log("=== Frontend Timeline Trim Session State Runtime ===");
  for (const [name, value] of Object.entries(checks)) {
    console.log(`${name}: ${value}`);
    assert.equal(value, true, `${name} failed`);
  }
  console.log(
    "\nDONE: Frontend timeline trim session state runtime test completed.",
  );
}

main();
