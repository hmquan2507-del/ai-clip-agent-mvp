/* eslint-disable @typescript-eslint/no-require-imports */

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
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
  buildReviewEditorViewModel,
} = require(path.resolve(
  __dirname,
  "../src/features/review/integration/adapters.ts",
));

function clip(clipId, startTime, endTime) {
  return {
    clip_id: clipId,
    track_id: "track-video",
    clip_type: "video",
    start_time: startTime,
    end_time: endTime,
    duration: endTime - startTime,
    source_start: 0,
    source_end: endTime - startTime,
    source_duration: endTime - startTime,
    text: clipId,
    opacity: 1,
    enabled: true,
    metadata: {},
  };
}

function runtimeState({ locked = false } = {}) {
  const snapshot = {
    session: {
      session_id: "session-1",
      production_id: "production-1",
      status: "ready",
      revision: 3,
      created_at: "2026-07-18T00:00:00Z",
      updated_at: "2026-07-18T00:00:00Z",
      metadata: {},
    },
    workspace: {
      production_id: "production-1",
      timeline: {},
      preview: {
        video_url: null,
        thumbnail_url: null,
      },
      ai: {
        suggestions: [],
        metadata: {},
      },
      metadata: {
        title: "Clipboard integration",
      },
    },
    timeline: {
      production_id: "production-1",
      duration: 20,
      fps: 30,
      minimum_clip_duration: 1 / 30,
      track_count: 1,
      clip_count: 2,
      dirty: false,
      revision: 3,
      tracks: [
        {
          track_id: "track-video",
          track_type: "video_primary",
          name: "Video chính",
          position: 0,
          locked,
          muted: false,
          clips: [
            clip("clip-1", 0, 5),
            clip("clip-2", 7, 12),
          ],
          metadata: {},
        },
      ],
      metadata: {},
    },
    preview: {
      source: {
        available: false,
        video_url: null,
      },
      state: {
        current_time: 8,
      },
      sync: {},
    },
    selection: {
      catalog: {},
      state: {
        selected_clip_ids: ["clip-1", "clip-2"],
        active_clip_id: "clip-2",
        cursor_time: 9.5,
      },
    },
    history: {
      can_undo: true,
      can_redo: false,
    },
    clipboard: {
      state: {
        available: true,
        item_count: 2,
      },
      content: {
        available: true,
        items: [],
      },
    },
    created_at: "2026-07-18T00:00:00Z",
    consistency: {
      production_ids_match: true,
      workspace_timeline_consistent: true,
    },
    metadata: {},
  };

  return {
    status: "ready",
    pendingOperation: null,
    pendingCommand: null,
    lastCommand: null,
    lastCommandResponse: null,
    pendingClipboardOperation: null,
    lastClipboardOperation: "copy",
    lastClipboardResponse: {
      clipboard: {
        history_state: {
          entry_count: 2,
          maximum_history_size: 20,
          latest_entry_id: "entry-2",
        },
      },
    },
    productionId: "production-1",
    sessionId: "session-1",
    session: snapshot.session,
    snapshot,
    error: null,
    requestRevision: 4,
    stateRevision: 4,
    updatedAt: "2026-07-18T00:00:00Z",
  };
}

function read(relativePath) {
  return fs.readFileSync(
    path.resolve(
      __dirname,
      "../src/features/review",
      relativePath,
    ),
    "utf8",
  );
}

function main() {
  const state = runtimeState();
  const sourceSnapshot = structuredClone(state.snapshot);
  const view = buildReviewEditorViewModel(state);
  const lockedView = buildReviewEditorViewModel(
    runtimeState({ locked: true }),
  );

  view.timeline.clipboard.selectedClipIds.push("ui-only-change");

  const runtimeWorkspace = read("integration/runtime-workspace.tsx");
  const timeline = read("shell/timeline.tsx");
  const provider = read("react/provider.tsx");
  const stateRuntime = read("state/runtime.ts");

  const operations = [
    "copyTimelineClips",
    "cutTimelineClips",
    "pasteTimelineClips",
    "restoreTimelineClipboardHistory",
    "clearTimelineClipboard",
    "clearTimelineClipboardHistory",
  ];

  const checks = {
    multi_selection_derived:
      view.timeline.clipboard.selectedClipIds.slice(0, 2).join(",") ===
      "clip-1,clip-2",
    copy_available_for_selection:
      view.timeline.clipboard.canCopy === true,
    cut_available_for_editable_tracks:
      view.timeline.clipboard.canCut === true,
    locked_track_cut_blocked:
      lockedView.timeline.clipboard.canCopy === true &&
      lockedView.timeline.clipboard.canCut === false,
    paste_uses_backend_cursor:
      view.timeline.clipboard.pasteTime === 9.5,
    clipboard_content_authoritative:
      view.timeline.clipboard.available === true &&
      view.timeline.clipboard.itemCount === 2 &&
      view.timeline.clipboard.canPaste === true,
    clipboard_history_authoritative:
      view.timeline.clipboard.historyEntryCount === 2 &&
      view.timeline.clipboard.latestHistoryEntryId === "entry-2" &&
      view.timeline.clipboard.canRestoreHistory === true,
    view_payload_isolated:
      JSON.stringify(state.snapshot) === JSON.stringify(sourceSnapshot) &&
      state.snapshot.selection.state.selected_clip_ids.length === 2,
    all_operations_cross_provider_boundary:
      operations.every(
        (operation) =>
          provider.includes(`runtime.${operation}`) &&
          runtimeWorkspace.includes(`actions.${operation}`),
      ),
    runtime_owns_expected_revision:
      stateRuntime.includes("expected_revision: revision") &&
      !runtimeWorkspace.includes("expected_revision"),
    pending_state_is_atomic:
      stateRuntime.includes('pendingOperation: "clipboard_command"') &&
      timeline.includes("clipboardControlsDisabled") &&
      timeline.includes("clipboardPending"),
    selection_remains_backend_authoritative:
      !timeline.includes("selected_clip_ids.push") &&
      !runtimeWorkspace.includes("selected_clip_ids.push"),
    shell_has_no_direct_api_calls:
      !timeline.includes("fetch(") &&
      !runtimeWorkspace.includes("fetch(") &&
      !timeline.includes("/api/"),
    shell_has_no_direct_timeline_mutation:
      !timeline.includes("timeline.tracks.push") &&
      !timeline.includes("timeline.tracks.splice") &&
      !runtimeWorkspace.includes("timeline.tracks.push"),
  };

  console.log("=== Timeline Clipboard UI Integration & Regression ===");

  for (const [name, value] of Object.entries(checks)) {
    console.log(`${name}: ${value}`);
    assert.equal(value, true, `${name} failed`);
  }

  console.log(
    "\nDONE: Timeline Clipboard UI integration and regression test completed.",
  );
}

main();
