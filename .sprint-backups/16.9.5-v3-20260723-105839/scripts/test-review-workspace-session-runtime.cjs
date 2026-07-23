/* eslint-disable @typescript-eslint/no-require-imports */

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const ts = require("typescript");

require.extensions[".ts"] = function compileTypeScript(
  module,
  filename,
) {
  const source = fs.readFileSync(
    filename,
    "utf8",
  );

  const output = ts.transpileModule(source, {
    fileName: filename,
    compilerOptions: {
      target: ts.ScriptTarget.ES2022,
      module: ts.ModuleKind.CommonJS,
      moduleResolution:
        ts.ModuleResolutionKind.NodeJs,
      esModuleInterop: true,
    },
  });

  module._compile(
    output.outputText,
    filename,
  );
};

const {
  ReviewWorkspaceAPIError,
} = require(path.resolve(
  __dirname,
  "../src/features/review/api/index.ts",
));

const {
  createReviewWorkspaceSessionRuntime,
} = require(path.resolve(
  __dirname,
  "../src/features/review/state/index.ts",
));

const productionId =
  "221e4b01-5fb9-4b4a-a549-4fb32c455059";

const sessionId = "session-1";

function session(
  status = "ready",
  revision = 1,
) {
  return {
    session_id: sessionId,
    production_id: productionId,
    status,
    active: status === "ready",
    ready: status === "ready",
    closed: status === "closed",
    timeline_revision: revision,
    dirty: revision > 1,
    revision,
    created_at:
      "2026-07-14T00:00:00.000Z",
    updated_at:
      "2026-07-14T00:00:00.000Z",
    closed_at:
      status === "closed"
        ? "2026-07-14T00:00:01.000Z"
        : null,
    error: null,
    metadata: {},
  };
}

function snapshot(revision = 1) {
  return {
    session:
      session("ready", revision),
    workspace: {
      production_id: productionId,
      metadata: {},
    },
    timeline: {
      production_id: productionId,
      revision,
      metadata: {
        marker: `revision-${revision}`,
      },
    },
    preview: {},
    selection: {},
    history: {},
    clipboard: {},
    created_at:
      "2026-07-14T00:00:00.000Z",
    consistency: {
      production_ids_match: true,
      workspace_timeline_consistent: true,
    },
    metadata: {},
  };
}

function response(operation, extra) {
  return {
    contract_version: "16.2.3",
    success: true,
    operation,
    production_id: productionId,
    session_id: sessionId,
    metadata: {},
    ...extra,
  };
}

function buildClient() {
  const calls = [];

  return {
    calls,

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

      return response("open_session", {
        session: session(),
        snapshot: snapshot(),
      });
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

      return response(
        "get_snapshot",
        {
          snapshot: snapshot(2),
        },
      );
    },

    async resetSession(
      currentProductionId,
      request,
      options,
    ) {
      calls.push({
        operation: "reset",
        currentProductionId,
        request,
        options,
      });

      return response(
        "reset_session",
        {
          snapshot: snapshot(1),
        },
      );
    },

    async closeSession(
      currentProductionId,
      request,
      options,
    ) {
      calls.push({
        operation: "close",
        currentProductionId,
        request,
        options,
      });

      return response(
        "close_session",
        {
          state:
            session("closed", 1),
          event: null,
        },
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

  const transitions = [];

  const unsubscribe = runtime.subscribe(
    (state) => {
      transitions.push(state.status);

      if (state.snapshot) {
        state.snapshot.metadata
          .listener_mutation = true;
      }
    },
  );

  const initial = runtime.getState();

  const initialValid =
    initial.status === "idle" &&
    initial.sessionId === null &&
    initial.snapshot === null;

  const opened =
    await runtime.open(productionId);

  const openValid =
    opened.status === "ready" &&
    opened.productionId ===
      productionId &&
    opened.sessionId === sessionId &&
    client.calls[0].operation === "open";

  const clonedState =
    runtime.getState();

  clonedState.snapshot.metadata
    .external_mutation = true;

  const currentState =
    runtime.getState();

  const snapshotIsolated =
    currentState.snapshot.metadata
      .external_mutation === undefined &&
    currentState.snapshot.metadata
      .listener_mutation === undefined;

  const refreshed =
    await runtime.refresh();

  const refreshValid =
    refreshed.status === "ready" &&
    refreshed.snapshot.timeline
      .revision === 2 &&
    refreshed.session
      .timeline_revision === 2;

  const reset =
    await runtime.reset();

  const resetValid =
    reset.status === "ready" &&
    reset.snapshot.timeline
      .revision === 1 &&
    client.calls[2].request
      .session_id === sessionId;

  const closed =
    await runtime.close();

  const closeValid =
    closed.status === "closed" &&
    closed.session.closed === true &&
    closed.snapshot === null;

  let closedOperationBlocked = false;

  try {
    await runtime.refresh();
  } catch (error) {
    closedOperationBlocked =
      error instanceof
        ReviewWorkspaceAPIError &&
      error.code ===
        "review_session_not_found";
  }

  const cleared =
    runtime.clear();

  const clearValid =
    cleared.status === "idle" &&
    cleared.productionId === null &&
    cleared.sessionId === null;

  const errorClient = buildClient();

  errorClient.openSession =
    async () => {
      throw new ReviewWorkspaceAPIError(
        "Production missing.",
        {
          code: "production_not_found",
          status: 404,
          productionId,
        },
      );
    };

  const errorRuntime =
    createReviewWorkspaceSessionRuntime({
      client: errorClient,
    });

  let errorMapped = false;

  try {
    await errorRuntime.open(productionId);
  } catch {
    const errorState =
      errorRuntime.getState();

    errorMapped =
      errorState.status === "error" &&
      errorState.error.code ===
        "production_not_found" &&
      errorState.error.status === 404;
  }

  const pending = [];
  const staleClient = buildClient();

  staleClient.openSession =
    (currentProductionId) =>
      new Promise((resolve) => {
        pending.push({
          currentProductionId,
          resolve,
        });
      });

  const staleRuntime =
    createReviewWorkspaceSessionRuntime({
      client: staleClient,
    });

  const firstOpen =
    staleRuntime.open("production-old");

  const secondOpen =
    staleRuntime.open(productionId);

  pending[1].resolve(
    response("open_session", {
      session: session(),
      snapshot: snapshot(3),
    }),
  );

  await secondOpen;

  pending[0].resolve({
    ...response("open_session", {
      session: {
        ...session(),
        production_id:
          "production-old",
      },
      snapshot: {
        ...snapshot(9),
        session: {
          ...session(),
          production_id:
            "production-old",
        },
      },
    }),
    production_id: "production-old",
  });

  await firstOpen;

  const staleState =
    staleRuntime.getState();

  const staleResponseIgnored =
    staleState.productionId ===
      productionId &&
    staleState.snapshot.timeline
      .revision === 3;

  unsubscribe();

  runtime.dispose();
  errorRuntime.dispose();
  staleRuntime.dispose();

  let disposedBlocked = false;

  try {
    await runtime.open(productionId);
  } catch (error) {
    disposedBlocked =
      error instanceof Error &&
      error.message.includes("disposed");
  }

  const transitionsValid =
    transitions.includes("opening") &&
    transitions.includes("refreshing") &&
    transitions.includes("resetting") &&
    transitions.includes("closing") &&
    transitions.includes("closed");

  const checks = {
    initial_valid: initialValid,
    open_valid: openValid,
    snapshot_isolated:
      snapshotIsolated,
    refresh_valid: refreshValid,
    reset_valid: resetValid,
    close_valid: closeValid,
    closed_operation_blocked:
      closedOperationBlocked,
    clear_valid: clearValid,
    error_mapped: errorMapped,
    stale_response_ignored:
      staleResponseIgnored,
    transitions_valid:
      transitionsValid,
    disposed_blocked:
      disposedBlocked,
  };

  console.log(
    "=== Frontend Review Workspace Session Runtime ===",
  );

  for (
    const [name, value]
    of Object.entries(checks)
  ) {
    console.log(`${name}: ${value}`);

    assert.equal(
      value,
      true,
      `${name} failed`,
    );
  }

  console.log(
    "\nDONE: Frontend Review Workspace session runtime test completed.",
  );
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});