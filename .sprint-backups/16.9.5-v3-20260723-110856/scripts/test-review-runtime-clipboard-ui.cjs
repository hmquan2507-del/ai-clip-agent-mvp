/* eslint-disable @typescript-eslint/no-require-imports */

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const React = require("react");
const { renderToStaticMarkup } = require("react-dom/server");
const ts = require("typescript");

function compileTypeScript(module, filename) {
  const source = fs.readFileSync(filename, "utf8");
  const output = ts.transpileModule(source, {
    fileName: filename,
    compilerOptions: {
      target: ts.ScriptTarget.ES2022,
      module: ts.ModuleKind.CommonJS,
      moduleResolution: ts.ModuleResolutionKind.NodeJs,
      jsx: ts.JsxEmit.ReactJSX,
      esModuleInterop: true,
    },
  });

  module._compile(output.outputText, filename);
}

require.extensions[".ts"] = compileTypeScript;
require.extensions[".tsx"] = compileTypeScript;

const {
  ReviewWorkspaceProvider,
  useReviewTimelineClipboard,
  useReviewWorkspaceActions,
  useReviewWorkspaceStatus,
} = require(path.resolve(
  __dirname,
  "../src/features/review/react/index.ts",
));

const {
  ReviewTimelinePanel,
} = require(path.resolve(
  __dirname,
  "../src/features/review/shell/timeline.tsx",
));

const initialState = {
  status: "idle",
  pendingOperation: null,
  pendingCommand: null,
  lastCommand: null,
  lastCommandResponse: null,
  pendingClipboardOperation: null,
  lastClipboardOperation: null,
  lastClipboardResponse: null,
  productionId: null,
  sessionId: null,
  session: null,
  snapshot: null,
  error: null,
  requestRevision: 0,
  stateRevision: 0,
  updatedAt: null,
};

async function main() {
  const calls = [];
  const runtime = {
    getState: () => structuredClone(initialState),
    subscribe: () => () => undefined,
    copyTimelineClips: async (input) => {
      calls.push(["copy", structuredClone(input)]);
      return structuredClone(initialState);
    },
    cutTimelineClips: async (input) => {
      calls.push(["cut", structuredClone(input)]);
      return structuredClone(initialState);
    },
    pasteTimelineClips: async (input) => {
      calls.push(["paste", structuredClone(input)]);
      return structuredClone(initialState);
    },
    restoreTimelineClipboardHistory: async (input) => {
      calls.push(["restore_history", structuredClone(input)]);
      return structuredClone(initialState);
    },
    clearTimelineClipboard: async () => {
      calls.push(["clear_content", null]);
      return structuredClone(initialState);
    },
    clearTimelineClipboardHistory: async () => {
      calls.push(["clear_history", null]);
      return structuredClone(initialState);
    },
  };

  const captured = {};

  function Probe() {
    captured.actions = useReviewWorkspaceActions();
    captured.clipboard = useReviewTimelineClipboard();
    captured.status = useReviewWorkspaceStatus();
    return React.createElement("div", null, "clipboard-provider-ready");
  }

  const providerHtml = renderToStaticMarkup(
    React.createElement(
      ReviewWorkspaceProvider,
      {
        productionId: "production-1",
        runtime,
        autoOpen: false,
      },
      React.createElement(Probe),
    ),
  );

  await captured.clipboard.copyTimelineClips({ clip_ids: ["clip-1"] });
  await captured.clipboard.cutTimelineClips({ clip_ids: ["clip-1"] });
  await captured.clipboard.pasteTimelineClips({ at_time: 4.25 });
  await captured.clipboard.restoreTimelineClipboardHistory({ entry_id: "entry-1" });
  await captured.clipboard.clearTimelineClipboard();
  await captured.clipboard.clearTimelineClipboardHistory();

  const clipboardView = {
    selectedClipIds: ["clip-1"],
    pasteTime: 4.25,
    available: true,
    itemCount: 1,
    historyEntryCount: 1,
    latestHistoryEntryId: "entry-1",
    canCopy: true,
    canCut: true,
    canPaste: true,
    canClear: true,
    canRestoreHistory: true,
    canClearHistory: true,
  };

  const timelineHtml = renderToStaticMarkup(
    React.createElement(ReviewTimelinePanel, {
      view: {
        duration: 10,
        durationLabel: "00:10",
        trackCount: 0,
        clipCount: 0,
        playheadPercent: 42.5,
        rulerMarks: ["00:00", "00:10"],
        tracks: [],
        commandTarget: null,
        clipboard: clipboardView,
      },
      pendingCommand: null,
      pendingClipboardOperation: null,
      onSelectClip: () => undefined,
      onTimelineCommand: () => undefined,
      onClipboardCommand: () => undefined,
    }),
  );

  const root = path.resolve(__dirname, "../src/features/review");
  const integrationSource = fs.readFileSync(
    path.join(root, "integration/runtime-workspace.tsx"),
    "utf8",
  );
  const adapterSource = fs.readFileSync(
    path.join(root, "integration/adapters.ts"),
    "utf8",
  );
  const timelineSource = fs.readFileSync(
    path.join(root, "shell/timeline.tsx"),
    "utf8",
  );

  const actionNames = [
    "copyTimelineClips",
    "cutTimelineClips",
    "pasteTimelineClips",
    "restoreTimelineClipboardHistory",
    "clearTimelineClipboard",
    "clearTimelineClipboardHistory",
  ];

  const checks = {
    provider_rendered: providerHtml.includes("clipboard-provider-ready"),
    clipboard_hook_available:
      captured.clipboard === captured.actions,
    clipboard_actions_complete:
      actionNames.every((name) => typeof captured.actions[name] === "function"),
    provider_delegates_to_runtime:
      JSON.stringify(calls.map(([operation]) => operation)) ===
      JSON.stringify([
        "copy",
        "cut",
        "paste",
        "restore_history",
        "clear_content",
        "clear_history",
      ]),
    clipboard_status_available:
      captured.status.pendingClipboardOperation === null &&
      captured.status.executingClipboard === false,
    clipboard_controls_rendered:
      [
        "Sao chép clip đã chọn",
        "Cắt clip đã chọn",
        "Dán clip tại con trỏ",
        "Xóa nội dung clipboard",
        "Khôi phục clipboard gần nhất",
        "Xóa lịch sử clipboard",
      ].every((label) => timelineHtml.includes(label)),
    backend_selection_authoritative:
      adapterSource.includes("selection.selected_clip_ids") &&
      adapterSource.includes("snapshot.clipboard.state"),
    backend_cursor_authoritative:
      adapterSource.includes("selection.cursor_time"),
    runtime_workspace_delegates:
      actionNames.every((name) => integrationSource.includes(`actions.${name}`)),
    clipboard_pending_visible:
      timelineSource.includes("clipboardCommandLabel") &&
      timelineSource.includes("pendingClipboardOperation"),
    controls_disabled_atomically:
      timelineSource.includes("clipboardControlsDisabled") &&
      timelineSource.includes("clipboardPending"),
    no_direct_api_calls:
      !integrationSource.includes("fetch(") &&
      !timelineSource.includes("fetch("),
    no_direct_timeline_mutation:
      !timelineSource.includes("timeline.tracks.push") &&
      !timelineSource.includes("selected_clip_ids.push"),
  };

  console.log("=== React Clipboard Provider, Hooks & UI ===");

  for (const [name, value] of Object.entries(checks)) {
    console.log(`${name}: ${value}`);
    assert.equal(value, true, `${name} failed`);
  }

  console.log("\nDONE: React Clipboard Provider, Hooks & UI test completed.");
}

main();
