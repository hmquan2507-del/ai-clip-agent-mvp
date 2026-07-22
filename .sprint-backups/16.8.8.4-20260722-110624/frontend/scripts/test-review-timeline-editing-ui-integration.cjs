/* eslint-disable @typescript-eslint/no-require-imports */

const assert =
  require("node:assert/strict");

const fs =
  require("node:fs");

const path =
  require("node:path");

const {
  spawnSync,
} = require("node:child_process");

const frontendRoot =
  path.resolve(
    __dirname,
    "..",
  );

const reviewRoot =
  path.resolve(
    frontendRoot,
    "src/features/review",
  );

function read(relativePath) {
  return fs.readFileSync(
    path.resolve(
      reviewRoot,
      relativePath,
    ),
    "utf8",
  );
}

function matches(
  source,
  pattern,
) {
  return pattern.test(source);
}

function runRegressionScript(
  filename,
) {
  const absolutePath =
    path.resolve(
      __dirname,
      filename,
    );

  const result =
    spawnSync(
      process.execPath,
      [absolutePath],
      {
        cwd: frontendRoot,
        encoding: "utf8",
        env: process.env,
      },
    );

  if (result.stdout) {
    process.stdout.write(
      result.stdout,
    );
  }

  if (result.stderr) {
    process.stderr.write(
      result.stderr,
    );
  }

  return {
    filename,
    success:
      result.status === 0,
    status:
      result.status,
    signal:
      result.signal,
  };
}

function main() {
  const apiClient =
    read("api/client.ts");

  const stateRuntime =
    read("state/runtime.ts");

  const provider =
    read("react/provider.tsx");

  const runtimeWorkspace =
    read(
      "integration/runtime-workspace.tsx",
    );

  const adapters =
    read(
      "integration/adapters.ts",
    );

  const integrationContracts =
    read(
      "integration/contracts.ts",
    );

  const shell =
    read(
      "shell/review-editor-shell.tsx",
    );

  const topbar =
    read(
      "shell/editor-topbar.tsx",
    );

  const timeline =
    read(
      "shell/timeline.tsx",
    );

  const selectionPathComplete =
    matches(
      timeline,
      /onSelectClip\s*\(\s*\{/,
    ) &&
    matches(
      shell,
      /onSelectClip\s*=\s*\{\s*onSelectClip\s*\}/,
    ) &&
    matches(
      runtimeWorkspace,
      /actions\.selectClip\s*\(\s*\{/,
    ) &&
    matches(
      provider,
      /runtime\.selectClip\s*\(/,
    ) &&
    matches(
      stateRuntime,
      /this\.client\.selectClip\s*\(/,
    ) &&
    matches(
      apiClient,
      /\/selection\/clip/,
    );

  const commandPathComplete =
    matches(
      timeline,
      /onTimelineCommand\s*\?\.\s*\(\s*\{/,
    ) &&
    matches(
      shell,
      /onTimelineCommand\s*=\s*\{\s*onTimelineCommand\s*\}/,
    ) &&
    matches(
      runtimeWorkspace,
      /actions\.splitClip\s*\(\s*\{/,
    ) &&
    matches(
      runtimeWorkspace,
      /actions\.duplicateClip\s*\(\s*\{/,
    ) &&
    matches(
      runtimeWorkspace,
      /actions\.deleteClip\s*\(\s*\{/,
    ) &&
    matches(
      runtimeWorkspace,
      /actions\.closeGap\s*\(\s*\{/,
    );

  const undoRedoPathComplete =
    matches(
      topbar,
      /onClick\s*=\s*\{\s*onUndo\s*\}/,
    ) &&
    matches(
      topbar,
      /onClick\s*=\s*\{\s*onRedo\s*\}/,
    ) &&
    matches(
      shell,
      /onUndo\s*=\s*\{\s*onUndo\s*\}/,
    ) &&
    matches(
      shell,
      /onRedo\s*=\s*\{\s*onRedo\s*\}/,
    ) &&
    matches(
      runtimeWorkspace,
      /actions\.undoTimeline\s*\(\s*\)/,
    ) &&
    matches(
      runtimeWorkspace,
      /actions\.redoTimeline\s*\(\s*\)/,
    );

  const snapshotReturnPathComplete =
    matches(
      stateRuntime,
      /completeRequest\s*\(/,
    ) &&
    matches(
      stateRuntime,
      /completeTimelineCommand\s*\(/,
    ) &&
    matches(
      stateRuntime,
      /response\.snapshot/,
    ) &&
    matches(
      adapters,
      /requireSnapshot\s*\(\s*state\.snapshot/,
    );

  const backendSelectionAuthoritative =
    matches(
      adapters,
      /snapshot\.selection\.state/,
    ) &&
    matches(
      adapters,
      /selection\.selected_clip_ids/,
    ) &&
    matches(
      adapters,
      /selection\.active_clip_id/,
    ) &&
    matches(
      adapters,
      /selectedIds\.has\s*\(/,
    ) &&
    matches(
      timeline,
      /aria-pressed\s*=\s*\{\s*clip\.selected\s*\}/,
    );

  const commandContextDerivedFromSnapshot =
    matches(
      adapters,
      /buildCommandTarget\s*\(/,
    ) &&
    matches(
      adapters,
      /selection\.cursor_time/,
    ) &&
    matches(
      adapters,
      /timeline\.minimum_clip_duration/,
    ) &&
    matches(
      adapters,
      /findGapBeforeClip\s*\(/,
    ) &&
    matches(
      integrationContracts,
      /ReviewTimelineCommandTargetView/,
    );

  const expectedRevisionOwnedByRuntime =
    matches(
      stateRuntime,
      /requireTimelineRevision\s*\(/,
    ) &&
    matches(
      stateRuntime,
      /expected_revision\s*:/,
    ) &&
    !runtimeWorkspace.includes(
      "expected_revision",
    ) &&
    !timeline.includes(
      "expected_revision",
    ) &&
    !shell.includes(
      "expected_revision",
    );

  const pendingStateIntegrated =
    matches(
      runtimeWorkspace,
      /state\.status\s*===\s*"selecting"/,
    ) &&
    matches(
      runtimeWorkspace,
      /state\.status\s*===\s*"executing"/,
    ) &&
    matches(
      runtimeWorkspace,
      /state\.pendingCommand/,
    ) &&
    matches(
      timeline,
      /aria-busy\s*=\s*\{/,
    ) &&
    timeline.includes(
      "Đang chọn clip…",
    ) &&
    timeline.includes(
      "Đang chỉnh sửa…",
    );

  const lockedTrackProtected =
    matches(
      adapters,
      /editable\s*:\s*!track\.locked/,
    ) &&
    matches(
      adapters,
      /track\.locked\s*\?\s*null/,
    ) &&
    matches(
      timeline,
      /canEditTarget/,
    );

  const failedOperationKeepsWorkspace =
    matches(
      runtimeWorkspace,
      /if\s*\(\s*!state\.snapshot\s*\)/,
    ) &&
    !matches(
      runtimeWorkspace,
      /state\.status\s*===\s*"error"\s*\|\|\s*!state\.snapshot/,
    );

  const noOptimisticSelection =
    !timeline.includes(
      "useState(",
    ) &&
    !runtimeWorkspace.includes(
      "selected_clip_ids.push",
    ) &&
    !runtimeWorkspace.includes(
      "active_clip_id =",
    );

  const noDirectAPICalls =
    !timeline.includes(
      "fetch(",
    ) &&
    !shell.includes(
      "fetch(",
    ) &&
    !topbar.includes(
      "fetch(",
    ) &&
    !runtimeWorkspace.includes(
      "/api/",
    ) &&
    !runtimeWorkspace.includes(
      "/timeline/",
    ) &&
    !runtimeWorkspace.includes(
      "/selection/",
    );

  const noDirectTimelineMutation =
    !timeline.includes(
      "timeline.revision++",
    ) &&
    !timeline.includes(
      "clips.splice",
    ) &&
    !timeline.includes(
      "tracks.splice",
    ) &&
    !shell.includes(
      "timeline.revision++",
    ) &&
    !runtimeWorkspace.includes(
      "snapshot.timeline =",
    );

  const commandOperationsComplete = [
    "split_clip",
    "duplicate_clip",
    "delete_clip",
    "close_gap",
  ].every(
    (operation) =>
      integrationContracts.includes(
        `"${operation}"`,
      ) &&
      timeline.includes(
        `"${operation}"`,
      ),
  );

  const sourceChecks = {
    selection_path_complete:
      selectionPathComplete,

    command_path_complete:
      commandPathComplete,

    undo_redo_path_complete:
      undoRedoPathComplete,

    snapshot_return_path_complete:
      snapshotReturnPathComplete,

    backend_selection_authoritative:
      backendSelectionAuthoritative,

    command_context_from_snapshot:
      commandContextDerivedFromSnapshot,

    expected_revision_runtime_owned:
      expectedRevisionOwnedByRuntime,

    pending_state_integrated:
      pendingStateIntegrated,

    locked_track_protected:
      lockedTrackProtected,

    failed_operation_keeps_workspace:
      failedOperationKeepsWorkspace,

    no_optimistic_selection:
      noOptimisticSelection,

    no_direct_api_calls:
      noDirectAPICalls,

    no_direct_timeline_mutation:
      noDirectTimelineMutation,

    command_operations_complete:
      commandOperationsComplete,
  };

  console.log(
    "=== Timeline Editing UI Integration ===",
  );

  for (
    const [name, value]
    of Object.entries(sourceChecks)
  ) {
    console.log(
      `${name}: ${value}`,
    );

    assert.equal(
      value,
      true,
      `${name} failed`,
    );
  }

  console.log(
    "\n=== Timeline Editing UI Regression Scripts ===",
  );

  const regressionScripts = [
    "test-review-selection-api-state-runtime.cjs",
    "test-review-runtime-timeline-selection-ui.cjs",
    "test-review-timeline-command-state-runtime.cjs",
    "test-review-runtime-timeline-command-controls.cjs",
  ];

  const regressionResults =
    regressionScripts.map(
      runRegressionScript,
    );

  const allRegressionScriptsPassed =
    regressionResults.every(
      (result) =>
        result.success,
    );

  const regressionResultIsolated =
    regressionResults.every(
      (result) =>
        typeof result.filename ===
          "string" &&
        typeof result.success ===
          "boolean",
    );

  console.log(
    `all_regression_scripts_passed: ${allRegressionScriptsPassed}`,
  );

  console.log(
    `regression_results_isolated: ${regressionResultIsolated}`,
  );

  assert.equal(
    allRegressionScriptsPassed,
    true,
    "One or more Timeline Editing UI regression scripts failed.",
  );

  assert.equal(
    regressionResultIsolated,
    true,
    "Regression result contract is invalid.",
  );

  console.log(
    "\nDONE: Timeline Editing UI integration and regression test completed.",
  );
}

main();