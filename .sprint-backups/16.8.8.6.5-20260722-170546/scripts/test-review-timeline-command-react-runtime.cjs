/* eslint-disable @typescript-eslint/no-require-imports */

const assert =
  require("node:assert/strict");
const fs =
  require("node:fs");
const path =
  require("node:path");
const React =
  require("react");
const {
  renderToStaticMarkup,
} = require(
  "react-dom/server",
);
const ts =
  require("typescript");

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
  ReviewWorkspaceProvider,
  useReviewTimelineCommands,
  useReviewWorkspaceActions,
  useReviewWorkspaceStatus,
} = require(
  path.resolve(
    __dirname,
    "../src/features/review/react/index.ts",
  ),
);

const productionId =
  "221e4b01-5fb9-4b4a-a549-4fb32c455059";

function runtimeState() {
  return {
    status: "executing",
    pendingOperation:
      "timeline_command",
    pendingCommand:
      "move_clip",
    lastCommand: null,
    lastCommandResponse: null,
    productionId,
    sessionId: "session-1",
    session: null,
    snapshot: null,
    error: null,
    requestRevision: 2,
    stateRevision: 2,
    updatedAt:
      "2026-07-14T00:00:00Z",
  };
}

function buildRuntime() {
  const calls = [];
  const state = runtimeState();

  function command(
    operation,
    input,
    options,
  ) {
    calls.push({
      operation,
      input,
      options,
    });

    return Promise.resolve(
      structuredClone(state),
    );
  }

  return {
    calls,

    getState() {
      return structuredClone(
        state,
      );
    },

    subscribe() {
      return () => {};
    },

    open(options) {
      return command(
        "open",
        options,
      );
    },

    refresh(options) {
      return command(
        "refresh",
        options,
      );
    },

    reset(options) {
      return command(
        "reset",
        options,
      );
    },

    close(options) {
      return command(
        "close",
        options,
      );
    },

    clear() {
      calls.push({
        operation: "clear",
      });

      return structuredClone(
        state,
      );
    },

    moveClip(input, options) {
      return command(
        "move_clip",
        input,
        options,
      );
    },

    trimClipStart(
      input,
      options,
    ) {
      return command(
        "trim_clip_start",
        input,
        options,
      );
    },

    trimClipEnd(
      input,
      options,
    ) {
      return command(
        "trim_clip_end",
        input,
        options,
      );
    },

    splitClip(input, options) {
      return command(
        "split_clip",
        input,
        options,
      );
    },

    duplicateClip(
      input,
      options,
    ) {
      return command(
        "duplicate_clip",
        input,
        options,
      );
    },

    deleteClip(input, options) {
      return command(
        "delete_clip",
        input,
        options,
      );
    },

    closeGap(input, options) {
      return command(
        "close_gap",
        input,
        options,
      );
    },

    undoTimeline(options) {
      return command(
        "undo",
        undefined,
        options,
      );
    },

    redoTimeline(options) {
      return command(
        "redo",
        undefined,
        options,
      );
    },
  };
}

async function main() {
  const runtime =
    buildRuntime();

  const captured = {};

  function Probe() {
    const actions =
      useReviewWorkspaceActions();

    const commands =
      useReviewTimelineCommands();

    const status =
      useReviewWorkspaceStatus();

    captured.actions = actions;
    captured.commands = commands;
    captured.status = status;

    return React.createElement(
      "div",
      null,
      "timeline-command-provider",
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
        React.createElement(
          Probe,
        ),
      ),
    );

  const controller =
    new AbortController();

  await captured.commands.moveClip(
    {
      clip_id: "clip-1",
      new_start_time: 2,
    },
    {
      signal:
        controller.signal,
    },
  );

  await captured.commands
    .trimClipStart({
      clip_id: "clip-1",
      new_start_time: 1,
    });

  await captured.commands
    .trimClipEnd({
      clip_id: "clip-1",
      new_end_time: 4,
    });

  await captured.commands
    .splitClip({
      clip_id: "clip-1",
      split_time: 2,
    });

  await captured.commands
    .duplicateClip({
      clip_id: "clip-1",
      new_start_time: 5,
    });

  await captured.commands
    .deleteClip({
      clip_id: "clip-copy",
    });

  await captured.commands
    .closeGap({
      track_id: "track-video",
      gap_start: 4,
      gap_end: 5,
    });

  await captured.commands
    .undoTimeline();

  await captured.commands
    .redoTimeline();

  const expectedOperations = [
    "move_clip",
    "trim_clip_start",
    "trim_clip_end",
    "split_clip",
    "duplicate_clip",
    "delete_clip",
    "close_gap",
    "undo",
    "redo",
  ];

  const commandCalls =
    runtime.calls.filter(
      (call) =>
        expectedOperations.includes(
          call.operation,
        ),
    );

  const providerRendered =
    html.includes(
      "timeline-command-provider",
    );

  const allCommandsAvailable =
    expectedOperations.every(
      (operation) => {
        const methodByOperation = {
          move_clip: "moveClip",
          trim_clip_start:
            "trimClipStart",
          trim_clip_end:
            "trimClipEnd",
          split_clip: "splitClip",
          duplicate_clip:
            "duplicateClip",
          delete_clip: "deleteClip",
          close_gap: "closeGap",
          undo: "undoTimeline",
          redo: "redoTimeline",
        };

        return (
          typeof captured.commands[
            methodByOperation[
              operation
            ]
          ] === "function"
        );
      },
    );

  const allCommandsDelegated =
    commandCalls.length === 9 &&
    commandCalls.every(
      (call, index) =>
        call.operation ===
          expectedOperations[index],
    );

  const runtimeContextHidden =
    commandCalls.every(
      (call) =>
        !call.input ||
        (
          call.input.session_id ===
            undefined &&
          call.input
            .expected_revision ===
            undefined
        ),
    );

  const abortSignalForwarded =
    commandCalls[0].options
      .signal ===
    controller.signal;

  const statusMapped =
    captured.status.status ===
      "executing" &&
    captured.status.executing ===
      true &&
    captured.status
      .pendingOperation ===
      "timeline_command" &&
    captured.status
      .pendingCommand ===
      "move_clip";

  const actionsStableBoundary =
    captured.actions.moveClip ===
      captured.commands.moveClip &&
    captured.actions.undoTimeline ===
      captured.commands.undoTimeline;

  const checks = {
    provider_rendered:
      providerRendered,
    all_commands_available:
      allCommandsAvailable,
    all_commands_delegated:
      allCommandsDelegated,
    runtime_context_hidden:
      runtimeContextHidden,
    abort_signal_forwarded:
      abortSignalForwarded,
    status_mapped:
      statusMapped,
    actions_stable_boundary:
      actionsStableBoundary,
    server_render_read_only:
      runtime.calls.length === 9,
  };

  console.log(
    "=== React Timeline Command "
    + "Provider & Hooks ===",
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
    "\nDONE: React timeline command "
    + "provider and hooks test "
    + "completed.",
  );
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});