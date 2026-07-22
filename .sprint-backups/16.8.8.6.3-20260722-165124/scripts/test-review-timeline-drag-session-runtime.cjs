/* eslint-disable @typescript-eslint/no-require-imports */

const assert =
  require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const ts = require("typescript");

require.extensions[".ts"] =
  function compileTypeScript(
    module,
    filename,
  ) {
    const source = fs.readFileSync(
      filename,
      "utf8",
    );
    const output = ts.transpileModule(
      source,
      {
        fileName: filename,
        compilerOptions: {
          target: ts.ScriptTarget.ES2022,
          module: ts.ModuleKind.CommonJS,
          moduleResolution:
            ts.ModuleResolutionKind.NodeJs,
          esModuleInterop: true,
        },
      },
    );

    module._compile(
      output.outputText,
      filename,
    );
  };

const dragIndexPath = path.resolve(
  __dirname,
  "../src/features/review/drag/index.ts",
);
const runtimePath = path.resolve(
  __dirname,
  "../src/features/review/drag/runtime.ts",
);
const runtimeSource = fs.readFileSync(
  runtimePath,
  "utf8",
);

const {
  REVIEW_TIMELINE_DRAG_RUNTIME_CONTRACT_VERSION,
  createReviewTimelineDragSessionRuntime,
} = require(dragIndexPath);

const source = {
  clipId: "clip-1",
  trackId: "video-1",
  startTime: 2,
  endTime: 6,
  duration: 4,
};
const environment = {
  viewport: {
    left: 100,
    top: 200,
    width: 600,
    height: 160,
    scrollLeft: 0,
    contentWidth: 600,
  },
  timelineDuration: 20,
  fps: 30,
  lanes: [
    {
      trackId: "video-1",
      top: 200,
      height: 80,
      locked: false,
    },
    {
      trackId: "video-locked",
      top: 280,
      height: 80,
      locked: true,
    },
  ],
};
const armInput = {
  productionId: "production-1",
  timelineRevision: 7,
  source,
  pointer: {
    clientX: 175,
    clientY: 240,
  },
  environment,
};
const armInputBefore = structuredClone(
  armInput,
);

function main() {
  let sequence = 0;
  const transitions = [];
  const runtime =
    createReviewTimelineDragSessionRuntime({
      dragThreshold: 4,
      createSessionId: () =>
        `drag-${++sequence}`,
      now: () =>
        "2026-07-18T08:00:00.000Z",
    });

  const initial = runtime.getState();
  const unsubscribe = runtime.subscribe(
    (state, previous) => {
      transitions.push(
        `${previous.phase}->${state.phase}`,
      );
    },
  );

  const armed = runtime.arm(armInput);
  const belowThreshold = runtime.move({
    pointer: {
      clientX: 177,
      clientY: 240,
    },
  });

  let earlyCommitBlocked = false;
  try {
    runtime.prepareCommit();
  } catch {
    earlyCommitBlocked = true;
  }

  const dragging = runtime.move({
    pointer: {
      clientX: 355,
      clientY: 240,
    },
  });
  const intent = runtime.prepareCommit();
  const committing = runtime.getState();

  intent.newStartTime = 999;
  const intentIsolated =
    runtime.getState().commitIntent
      ?.newStartTime !== 999;

  let secondCommitBlocked = false;
  try {
    runtime.prepareCommit();
  } catch {
    secondCommitBlocked = true;
  }

  const completed = runtime.completeCommit();
  const cancelledStart = runtime.arm({
    ...armInput,
    timelineRevision: 8,
  });
  runtime.move({
    pointer: {
      clientX: 390,
      clientY: 240,
    },
  });
  const cancelled = runtime.cancel(
    "escape_pressed",
  );

  const isolatedSnapshot = runtime.getState();
  isolatedSnapshot.session.source.clipId =
    "changed-outside";
  isolatedSnapshot.environment.lanes[0]
    .trackId = "changed-outside";
  const snapshotIsolated =
    runtime.getState().session.source.clipId ===
      "clip-1" &&
    runtime.getState().environment.lanes[0]
      .trackId === "video-1";

  const lockedRuntime =
    createReviewTimelineDragSessionRuntime({
      dragThreshold: 0,
      createSessionId: () => "drag-locked",
    });
  lockedRuntime.arm(armInput);
  const lockedProjection = lockedRuntime.move({
    pointer: {
      clientX: 355,
      clientY: 320,
    },
  });

  let lockedCommitBlocked = false;
  try {
    lockedRuntime.prepareCommit();
  } catch {
    lockedCommitBlocked = true;
  }

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
      REVIEW_TIMELINE_DRAG_RUNTIME_CONTRACT_VERSION ===
        "16.5.2" &&
      initial.contractVersion === "16.5.2",
    initial_idle:
      initial.phase === "idle" &&
      initial.session === null,
    arm_valid:
      armed.phase === "armed" &&
      armed.session.sessionId === "drag-1" &&
      armed.session.timelineRevision === 7,
    below_threshold_stays_armed:
      belowThreshold.phase === "armed",
    early_commit_blocked:
      earlyCommitBlocked,
    drag_transition_valid:
      dragging.phase === "dragging" &&
      dragging.pointerDistance >= 4,
    projection_is_preview_only:
      dragging.projection.valid === true &&
      dragging.commitIntent === null,
    commit_intent_valid:
      committing.phase === "committing" &&
      committing.commitIntent.clipId === "clip-1" &&
      committing.commitIntent.targetTrackId ===
        "video-1" &&
      !("expected_revision" in
        committing.commitIntent),
    intent_isolated: intentIsolated,
    exactly_one_commit_prepared:
      secondCommitBlocked,
    completion_returns_idle:
      completed.phase === "idle" &&
      completed.session === null &&
      completed.lastCommittedIntent !== null,
    cancel_is_read_only:
      cancelledStart.session.timelineRevision === 8 &&
      cancelled.phase === "cancelled" &&
      cancelled.cancelReason ===
        "escape_pressed" &&
      cancelled.commitIntent === null,
    locked_projection_blocked:
      lockedProjection.projection.valid === false &&
      lockedProjection.projection.blockedReason ===
        "track_locked" &&
      lockedCommitBlocked,
    state_snapshots_isolated:
      snapshotIsolated,
    inputs_unchanged:
      JSON.stringify(armInput) ===
        JSON.stringify(armInputBefore),
    transitions_emitted_once:
      transitions.length === 9 &&
      transitions.includes(
        "dragging->committing",
      ) &&
      transitions.filter(
        (transition) =>
          transition ===
          "dragging->committing",
      ).length === 1,
    reset_valid:
      resetState.phase === "idle" &&
      resetState.cancelReason === null,
    disposed_blocked:
      disposedBlocked,
    no_api_or_timeline_mutation:
      !runtimeSource.includes("fetch(") &&
      !runtimeSource.includes("moveClip(") &&
      !runtimeSource.includes("expected_revision") &&
      !runtimeSource.includes("../api"),
  };

  console.log(
    "=== Frontend Timeline Drag Session State Runtime ===",
  );
  for (const [key, value] of
    Object.entries(checks)) {
    console.log(`${key}: ${value}`);
  }

  assert.equal(
    Object.values(checks).every(Boolean),
    true,
    JSON.stringify(checks, null, 2),
  );

  console.log(
    "\nDONE: Frontend timeline drag session state runtime test completed.",
  );
}

main();
