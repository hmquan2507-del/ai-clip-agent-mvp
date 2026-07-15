/* eslint-disable @typescript-eslint/no-require-imports */

const assert = require(
  "node:assert/strict",
);
const fs = require("node:fs");
const path = require("node:path");
const React = require("react");

const {
  renderToStaticMarkup,
} = require("react-dom/server");

const ts = require("typescript");

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
        target:
          ts.ScriptTarget.ES2022,
        module:
          ts.ModuleKind.CommonJS,
        moduleResolution:
          ts.ModuleResolutionKind
            .NodeJs,
        jsx:
          ts.JsxEmit.ReactJSX,
        esModuleInterop: true,
      },
    },
  );

  module._compile(
    output.outputText,
    filename,
  );
}

require.extensions[".ts"] =
  compileTypeScript;

require.extensions[".tsx"] =
  compileTypeScript;

const {
  createReviewWorkspaceSessionRuntime,
} = require(path.resolve(
  __dirname,
  "../src/features/review/state/index.ts",
));

const {
  ReviewWorkspaceProvider,
  useReviewClipboard,
  useReviewHistory,
  useReviewPreview,
  useReviewSelection,
  useReviewTimeline,
  useReviewWorkspace,
  useReviewWorkspaceActions,
  useReviewWorkspaceSession,
  useReviewWorkspaceSnapshot,
  useReviewWorkspaceStatus,
} = require(path.resolve(
  __dirname,
  "../src/features/review/react/index.ts",
));

const productionId =
  "221e4b01-5fb9-4b4a-a549-4fb32c455059";

const calls = [];

const client = {
  async openSession() {
    calls.push("open");

    throw new Error(
      "Not expected during server render.",
    );
  },

  async getSnapshot() {
    calls.push("refresh");

    throw new Error(
      "Not expected during server render.",
    );
  },

  async resetSession() {
    calls.push("reset");

    throw new Error(
      "Not expected during server render.",
    );
  },

  async closeSession() {
    calls.push("close");

    throw new Error(
      "Not expected during server render.",
    );
  },
};

function main() {
  const runtime =
    createReviewWorkspaceSessionRuntime({
      client,
    });

  const captured = {};

  function Probe() {
    const workspace =
      useReviewWorkspace();

    const actions =
      useReviewWorkspaceActions();

    const status =
      useReviewWorkspaceStatus();

    const session =
      useReviewWorkspaceSession();

    const snapshot =
      useReviewWorkspaceSnapshot();

    captured.runtimeMatches =
      workspace.runtime === runtime;

    captured.productionMatches =
      workspace.productionId ===
      productionId;

    captured.initialStatus =
      status.status;

    captured.loading =
      status.loading;

    captured.sessionId =
      session.sessionId;

    captured.snapshotAvailable =
      snapshot.available;

    captured.timeline =
      useReviewTimeline();

    captured.preview =
      useReviewPreview();

    captured.selection =
      useReviewSelection();

    captured.history =
      useReviewHistory();

    captured.clipboard =
      useReviewClipboard();

    captured.actions =
      Object.keys(actions).sort();

    return React.createElement(
      "div",
      null,
      "review-provider-ready",
    );
  }

  const html =
    renderToStaticMarkup(
      React.createElement(
        ReviewWorkspaceProvider,
        {
          productionId,
          runtime,
          autoOpen: false,
        },
        React.createElement(Probe),
      ),
    );

  let outsideProviderBlocked = false;

  function InvalidProbe() {
    useReviewWorkspace();
    return null;
  }

  try {
    renderToStaticMarkup(
      React.createElement(
        InvalidProbe,
      ),
    );
  } catch (error) {
    outsideProviderBlocked =
      error instanceof Error &&
      error.message.includes(
        "ReviewWorkspaceProvider",
      );
  }

  const checks = {
    provider_rendered:
      html.includes(
        "review-provider-ready",
      ),

    runtime_injected:
      captured.runtimeMatches === true,

    production_id_available:
      captured.productionMatches === true,

    initial_status_valid:
      captured.initialStatus ===
        "idle" &&
      captured.loading === false,

    session_initially_empty:
      captured.sessionId === null,

    snapshot_initially_empty:
      captured.snapshotAvailable ===
        false &&
      captured.timeline === null &&
      captured.preview === null &&
      captured.selection === null &&
      captured.history === null &&
      captured.clipboard === null,

    actions_complete:
      JSON.stringify(
        captured.actions,
      ) ===
      JSON.stringify([
  "clear",
  "close",
  "closeGap",
  "deleteClip",
  "duplicateClip",
  "moveClip",
  "open",
  "redoTimeline",
  "refresh",
  "reset",
  "splitClip",
  "trimClipEnd",
  "trimClipStart",
  "undoTimeline",
]),

    outside_provider_blocked:
      outsideProviderBlocked,

    server_render_read_only:
      calls.length === 0,
  };

  console.log(
    "=== React Review Workspace Provider & Hooks ===",
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

  runtime.dispose();

  console.log(
    "\nDONE: React Review Workspace Provider & Hooks test completed.",
  );
}

main();