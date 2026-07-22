/* eslint-disable @typescript-eslint/no-require-imports */

const assert =
  require("node:assert/strict");
const fs =
  require("node:fs");
const path =
  require("node:path");
const ts =
  require("typescript");

require.extensions[".ts"] =
  function compileTypeScript(
    module,
    filename,
  ) {
    const source =
      fs.readFileSync(
        filename,
        "utf8",
      );

    const output =
      ts.transpileModule(
        source,
        {
          fileName: filename,
          compilerOptions: {
            target:
              ts.ScriptTarget.ES2022,
            module:
              ts.ModuleKind.CommonJS,
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

const {
  ReviewWorkspaceAPIError,
} = require(
  path.resolve(
    __dirname,
    "../src/features/review/api/index.ts",
  ),
);

const {
  createReviewWorkspaceSessionRuntime,
} = require(
  path.resolve(
    __dirname,
    "../src/features/review/state/index.ts",
  ),
);

const productionId =
  "221e4b01-5fb9-4b4a-a549-4fb32c455059";
const sessionId = "session-1";

function session(revision) {
  return {
    session_id: sessionId,
    production_id: productionId,
    status: "ready",
    active: true,
    ready: true,
    closed: false,
    timeline_revision: revision,
    dirty: revision > 1,
    revision,
    created_at:
      "2026-07-14T00:00:00Z",
    updated_at:
      "2026-07-14T00:00:00Z",
    closed_at: null,
    error: null,
    metadata: {},
  };
}

function snapshot(revision) {
  return {
    session: session(revision),
    workspace: {
      production_id: productionId,
      metadata: {},
    },
    timeline: {
      production_id: productionId,
      revision,
      metadata: {
        marker:
          `revision-${revision}`,
      },
    },
    preview: {},
    selection: {},
    history: {
      current_revision: revision,
    },
    clipboard: {},
    created_at:
      "2026-07-14T00:00:00Z",
    consistency: {
      production_ids_match: true,
      workspace_timeline_consistent: true,
    },
    metadata: {},
  };
}

function lifecycleResponse(
  operation,
  revision,
) {
  return {
    contract_version: "16.2.3",
    success: true,
    operation,
    production_id: productionId,
    session_id: sessionId,
    session: session(revision),
    snapshot: snapshot(revision),
    metadata: {},
  };
}

function commandResponse(
  operation,
  revision,
) {
  return {
    contract_version: "16.4.1",
    success: true,
    operation,
    production_id: productionId,
    session_id: sessionId,
    snapshot: snapshot(revision),
    command: {
      command_id:
        `command-${operation}`,
    },
    event: {
      action: "execute",
      operation_type: operation,
    },
    history: {
      current_revision: revision,
      can_undo: true,
      can_redo: false,
    },
    metadata: {
      current_revision: revision,
    },
  };
}

function buildClient() {
  const calls = [];
  let revision = 1;
  let refreshRevision = 1;

  function execute(
    operation,
    currentProductionId,
    request,
    options,
  ) {
    calls.push({
      operation,
      currentProductionId,
      request,
      options,
    });

    revision += 1;

    return Promise.resolve(
      commandResponse(
        operation,
        revision,
      ),
    );
  }

  return {
    calls,

    setRefreshRevision(value) {
      refreshRevision = value;
    },

    async openSession(
      currentProductionId,
      request,
      options,
    ) {
      calls.push({
        operation: "open",
        currentProductionId,
        request,
        options,
      });

      return lifecycleResponse(
        "open_session",
        revision,
      );
    },

    async getSnapshot(
      currentProductionId,
      currentSessionId,
      options,
    ) {
      calls.push({
        operation: "refresh",
        currentProductionId,
        currentSessionId,
        options,
      });

      revision = refreshRevision;

      return {
        contract_version: "16.2.3",
        success: true,
        operation: "get_snapshot",
        production_id: productionId,
        session_id: sessionId,
        snapshot:
          snapshot(refreshRevision),
        metadata: {},
      };
    },

    moveClip(
      productionIdValue,
      request,
      options,
    ) {
      return execute(
        "move_clip",
        productionIdValue,
        request,
        options,
      );
    },

    trimClipStart(
      productionIdValue,
      request,
      options,
    ) {
      return execute(
        "trim_clip_start",
        productionIdValue,
        request,
        options,
      );
    },

    trimClipEnd(
      productionIdValue,
      request,
      options,
    ) {
      return execute(
        "trim_clip_end",
        productionIdValue,
        request,
        options,
      );
    },

    splitClip(
      productionIdValue,
      request,
      options,
    ) {
      return execute(
        "split_clip",
        productionIdValue,
        request,
        options,
      );
    },

    duplicateClip(
      productionIdValue,
      request,
      options,
    ) {
      return execute(
        "duplicate_clip",
        productionIdValue,
        request,
        options,
      );
    },

    deleteClip(
      productionIdValue,
      request,
      options,
    ) {
      return execute(
        "delete_clip",
        productionIdValue,
        request,
        options,
      );
    },

    closeGap(
      productionIdValue,
      request,
      options,
    ) {
      return execute(
        "close_gap",
        productionIdValue,
        request,
        options,
      );
    },

    undoTimeline(
      productionIdValue,
      request,
      options,
    ) {
      return execute(
        "undo",
        productionIdValue,
        request,
        options,
      );
    },

    redoTimeline(
      productionIdValue,
      request,
      options,
    ) {
      return execute(
        "redo",
        productionIdValue,
        request,
        options,
      );
    },

    async resetSession() {
      throw new Error(
        "Not used in this test.",
      );
    },

    async closeSession() {
      throw new Error(
        "Not used in this test.",
      );
    },
  };
}

async function main() {
  const client = buildClient();

  const runtime =
    createReviewWorkspaceSessionRuntime({
      client,
    });

  await runtime.open(productionId);

  const initial =
    runtime.getState();

  const initialReady =
    initial.status === "ready" &&
    initial.snapshot.timeline
      .revision === 1;

  const transitions = [];

  const unsubscribe =
    runtime.subscribe((state) => {
      transitions.push({
        status: state.status,
        pendingCommand:
          state.pendingCommand,
      });

      if (state.snapshot) {
        state.snapshot.metadata
          .listener_mutation = true;
      }
    });

  const moved =
    await runtime.moveClip({
      clip_id: "clip-1",
      new_start_time: 2,
      target_track_id:
        "track-video",
    });

  const moveValid =
    moved.status === "ready" &&
    moved.pendingOperation === null &&
    moved.pendingCommand === null &&
    moved.lastCommand ===
      "move_clip" &&
    moved.snapshot.timeline
      .revision === 2 &&
    moved.session.timeline_revision ===
      2;

  const moveCall =
    client.calls.find(
      (call) =>
        call.operation ===
        "move_clip",
    );

  const runtimeOwnsContext =
    moveCall.request.session_id ===
      sessionId &&
    moveCall.request
      .expected_revision === 1;

  await runtime.trimClipStart({
    clip_id: "clip-1",
    new_start_time: 1,
  });

  await runtime.trimClipEnd({
    clip_id: "clip-1",
    new_end_time: 4,
  });

  await runtime.splitClip({
    clip_id: "clip-1",
    split_time: 2,
  });

  await runtime.duplicateClip({
    clip_id: "clip-1",
    new_start_time: 5,
  });

  await runtime.deleteClip({
    clip_id: "clip-copy",
    close_gap: false,
  });

  await runtime.closeGap({
    track_id: "track-video",
    gap_start: 4,
    gap_end: 5,
  });

  await runtime.undoTimeline();
  const finalState =
    await runtime.redoTimeline();

  const allCommandsOperational =
    finalState.lastCommand === "redo" &&
    finalState.snapshot.timeline
      .revision === 10;

  const executingTransitionValid =
    transitions.some(
      (transition) =>
        transition.status ===
          "executing" &&
        transition.pendingCommand ===
          "move_clip",
    );

  const cloned =
    runtime.getState();

  cloned.snapshot.metadata
    .external_mutation = true;

  const stateIsolated =
    runtime.getState()
      .snapshot.metadata
      .external_mutation ===
        undefined &&
    runtime.getState()
      .snapshot.metadata
      .listener_mutation ===
        undefined;

  const failureSnapshot =
    runtime.getState().snapshot;

  client.deleteClip = async () => {
    throw new ReviewWorkspaceAPIError(
      "Synthetic command failure.",
      {
        code:
          "review_session_operation_failed",
        status: 409,
        productionId,
        sessionId,
      },
    );
  };

  let failureMapped = false;

  try {
    await runtime.deleteClip({
      clip_id: "missing",
    });
  } catch {
    const failed =
      runtime.getState();

    failureMapped =
      failed.status === "error" &&
      failed.error.code ===
        "review_session_operation_failed" &&
      failed.snapshot.timeline
        .revision ===
        failureSnapshot.timeline.revision;
  }

  const conflictClient =
    buildClient();

  conflictClient.setRefreshRevision(
    12,
  );

  conflictClient.moveClip =
    async () => {
      throw new ReviewWorkspaceAPIError(
        "Revision conflict.",
        {
          code:
            "review_session_conflict",
          status: 409,
          productionId,
          sessionId,
          metadata: {
            application_error: {
              expected_revision: 1,
              current_revision: 12,
            },
          },
        },
      );
    };

  const conflictRuntime =
    createReviewWorkspaceSessionRuntime({
      client: conflictClient,
    });

  await conflictRuntime.open(
    productionId,
  );

  let conflictRecovered = false;

  try {
    await conflictRuntime.moveClip({
      clip_id: "clip-1",
      new_start_time: 2,
    });
  } catch {
    const recovered =
      conflictRuntime.getState();

    const moveCalls =
      conflictClient.calls.filter(
        (call) =>
          call.operation ===
          "move_clip",
      );

    conflictRecovered =
      recovered.status === "ready" &&
      recovered.snapshot.timeline
        .revision === 12 &&
      recovered.error
        .isRevisionConflict === true &&
      recovered.error
        .expectedRevision === 1 &&
      recovered.error
        .currentRevision === 12 &&
      moveCalls.length === 0;
  }

  const pending = [];
  const staleClient =
    buildClient();

  staleClient.moveClip =
    (
      currentProductionId,
      request,
      options,
    ) =>
      new Promise((resolve) => {
        staleClient.calls.push({
          operation: "move_clip",
          currentProductionId,
          request,
          options,
        });

        pending.push(resolve);
      });

  const staleRuntime =
    createReviewWorkspaceSessionRuntime({
      client: staleClient,
    });

  await staleRuntime.open(
    productionId,
  );

  const pendingCommand =
    staleRuntime.moveClip({
      clip_id: "clip-1",
      new_start_time: 2,
    });

  let concurrentBlocked = false;

  try {
    await staleRuntime.undoTimeline();
  } catch (error) {
    concurrentBlocked =
      error instanceof
        ReviewWorkspaceAPIError &&
      error.code ===
        "review_session_conflict";
  }

  staleRuntime.clear();

  pending[0](
    commandResponse(
      "move_clip",
      99,
    ),
  );

  await pendingCommand;

  const staleResponseIgnored =
    staleRuntime.getState().status ===
      "idle" &&
    staleRuntime.getState()
      .snapshot === null;

  unsubscribe();

  runtime.dispose();
  conflictRuntime.dispose();
  staleRuntime.dispose();

  const checks = {
    initial_ready: initialReady,
    move_valid: moveValid,
    runtime_owns_context:
      runtimeOwnsContext,
    all_commands_operational:
      allCommandsOperational,
    executing_transition_valid:
      executingTransitionValid,
    state_isolated: stateIsolated,
    failure_mapped: failureMapped,
    conflict_recovered:
      conflictRecovered,
    concurrent_command_blocked:
      concurrentBlocked,
    stale_response_ignored:
      staleResponseIgnored,
  };

  console.log(
    "=== Frontend Timeline "
    + "Command State Runtime ===",
  );

  for (
    const [name, value]
    of Object.entries(checks)
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
    "\nDONE: Frontend timeline "
    + "command state runtime "
    + "test completed.",
  );
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});