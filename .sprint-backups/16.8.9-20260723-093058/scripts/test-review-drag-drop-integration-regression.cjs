/* eslint-disable @typescript-eslint/no-require-imports */

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const {
  spawnSync,
} = require("node:child_process");

const frontendRoot = path.resolve(
  __dirname,
  "..",
);
const reviewRoot = path.resolve(
  frontendRoot,
  "src/features/review",
);

const regressionScripts = [
  "test-review-timeline-drag-coordinate-model.cjs",
  "test-review-timeline-drag-session-runtime.cjs",
  "test-review-timeline-snap-runtime.cjs",
  "test-review-runtime-clip-drag-ui.cjs",
  "test-review-cross-track-drag-drop.cjs",
  "test-review-drag-preview-cancel-conflict-recovery.cjs",
  "test-review-timeline-command-state-runtime.cjs",
];

function read(relativePath) {
  return fs.readFileSync(
    path.resolve(
      reviewRoot,
      relativePath,
    ),
    "utf8",
  );
}

function runRegressionScript(filename) {
  const result = spawnSync(
    process.execPath,
    [path.resolve(__dirname, filename)],
    {
      cwd: frontendRoot,
      encoding: "utf8",
      env: process.env,
    },
  );

  if (result.stdout) {
    process.stdout.write(result.stdout);
  }

  if (result.stderr) {
    process.stderr.write(result.stderr);
  }

  assert.equal(
    result.status,
    0,
    `${filename} exited with status ${result.status}`,
  );

  return filename;
}

function includesAll(source, values) {
  return values.every(
    (value) => source.includes(value),
  );
}

function count(source, value) {
  return source.split(value).length - 1;
}

function main() {
  const completedScripts =
    regressionScripts.map(
      runRegressionScript,
    );

  const dragContracts = read(
    "drag/contracts.ts",
  );
  const dragRuntime = read(
    "drag/runtime.ts",
  );
  const coordinates = read(
    "drag/coordinates.ts",
  );
  const compatibility = read(
    "drag/compatibility.ts",
  );
  const snapRuntime = read(
    "drag/snap-runtime.ts",
  );
  const dragHook = read(
    "integration/use-runtime-clip-drag.ts",
  );
  const runtimeWorkspace = read(
    "integration/runtime-workspace.tsx",
  );
  const adapters = read(
    "integration/adapters.ts",
  );
  const timeline = read(
    "shell/timeline.tsx",
  );
  const shell = read(
    "shell/review-editor-shell.tsx",
  );
  const stateRuntime = read(
    "state/runtime.ts",
  );
  const workspaceRegression =
    fs.readFileSync(
      path.resolve(
        __dirname,
        "test-review-workspace-regression.cjs",
      ),
      "utf8",
    );

  const forbiddenDirectMutation = [
    "start_time =",
    "end_time =",
    "track_id =",
    "timeline.tracks.push",
    "timeline.tracks.splice",
    "selected_clip_ids.push",
  ];
  const uiBoundarySource = [
    timeline,
    shell,
    runtimeWorkspace,
    dragHook,
  ].join("\n");

  const checks = {
    drag_regressions_complete:
      completedScripts.length ===
        regressionScripts.length,

    contracts_and_runtime_connected:
      includesAll(dragContracts, [
        "ReviewTimelineDragSession",
        "ReviewTimelineMoveIntent",
        "ReviewTimelineDragFailure",
      ]) &&
      includesAll(dragRuntime, [
        "prepareCommit()",
        "completeCommit()",
        "failCommit(",
        "cancel(",
      ]),

    coordinate_and_snap_models_used:
      dragRuntime.includes(
        "projectReviewTimelineClipMove",
      ) &&
      dragRuntime.includes(
        "this.snapProjector.project(",
      ) &&
      coordinates.includes(
        "evaluateReviewTimelineTrackCompatibility",
      ) &&
      snapRuntime.includes(
        "clip.trackId !== targetTrackId",
      ),

    same_and_cross_track_supported:
      compatibility.includes(
        "video_overlay",
      ) &&
      dragHook.includes(
        "lanes: geometry.lanes",
      ) &&
      dragHook.includes(
        "target_track_id:",
      ) &&
      timeline.includes(
        'data-review-cross-track-ghost="true"',
      ),

    locked_and_incompatible_read_only:
      coordinates.includes(
        '"track_locked"',
      ) &&
      coordinates.includes(
        '"incompatible_track"',
      ) &&
      dragHook.includes(
        'runtime.cancel("invalid_drop")',
      ),

    exactly_one_command_boundary:
      count(dragHook, "await moveClip({") === 1 &&
      dragHook.includes(
        "const intent = runtime.prepareCommit()",
      ) &&
      dragHook.includes(
        "runtime.completeCommit()",
      ) &&
      !dragHook.includes(
        "expected_revision",
      ),

    authoritative_conflict_recovery:
      dragHook.includes(
        "error.isRevisionConflict",
      ) &&
      dragHook.includes(
        "runtime.failCommit(",
      ) &&
      stateRuntime.includes(
        "recoverRevisionConflict(",
      ) &&
      stateRuntime.includes(
        "await this.client.getSnapshot(",
      ) &&
      !dragHook.includes("getSnapshot(") &&
      !dragHook.includes("refresh(") &&
      !dragHook.includes("retryMoveClip"),

    cancel_never_commits:
      includesAll(timeline, [
        "onPointerCancel",
        '"pointer_cancelled"',
        '"escape_pressed"',
        "releasePointerCapture",
      ]) &&
      dragRuntime.includes(
        "commitIntent: null",
      ),

    preview_is_not_timeline_state:
      timeline.includes(
        "dragProjection",
      ) &&
      timeline.includes(
        "projectedStartTime",
      ) &&
      adapters.includes(
        "snapshot.selection.state",
      ) &&
      !timeline.includes("useState("),

    interaction_boundaries_preserved:
      runtimeWorkspace.includes(
        "useReviewRuntimeClipDrag",
      ) &&
      runtimeWorkspace.includes(
        "actions.moveClip",
      ) &&
      shell.includes(
        "onClipDragStart",
      ) &&
      timeline.includes(
        "Boolean(drag?.active)",
      ),

    no_direct_api_or_timeline_mutation:
      !uiBoundarySource.includes("fetch(") &&
      !uiBoundarySource.includes("/api/") &&
      forbiddenDirectMutation.every(
        (value) =>
          !uiBoundarySource.includes(value),
      ),

    master_regression_registered:
      workspaceRegression.includes(
        '"test-review-drag-drop-integration-regression.cjs"',
      ),
  };

  console.log(
    "=== Drag & Drop Integration & Regression ===",
  );

  for (const [name, value] of
    Object.entries(checks)) {
    console.log(`${name}: ${value}`);
    assert.equal(
      value,
      true,
      `${name} failed`,
    );
  }

  console.log(
    "\nDONE: Drag and drop integration " +
      "and regression test completed.",
  );
}

main();
