/* eslint-disable @typescript-eslint/no-require-imports */

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const frontendRoot = path.resolve(__dirname, "..");

function read(relativePath) {
  return fs.readFileSync(
    path.join(frontendRoot, relativePath),
    "utf8",
  );
}

function main() {
  const hook = read(
    "src/features/review/integration/use-runtime-keyboard-editing.ts",
  );
  const contracts = read(
    "src/features/review/integration/contracts.ts",
  );
  const integrationIndex = read(
    "src/features/review/integration/index.ts",
  );
  const workspace = read(
    "src/features/review/integration/runtime-workspace.tsx",
  );
  const shell = read(
    "src/features/review/shell/review-editor-shell.tsx",
  );

  const checks = {
    keyboard_view_contract_valid:
      contracts.includes("ReviewRuntimeKeyboardEditingView") &&
      contracts.includes("ReviewTimelineKeyboardRuntimeState") &&
      contracts.includes("ReviewTimelineKeyboardOperation"),
    runtime_hook_available:
      hook.includes("useReviewRuntimeKeyboardEditing") &&
      integrationIndex.includes(
        'export * from "./use-runtime-keyboard-editing"',
      ),
    runtime_owns_shortcut_session:
      hook.includes("createReviewTimelineKeyboardShortcutRuntime") &&
      hook.includes("runtime.handleKeyDown(") &&
      hook.includes("runtime.handleKeyUp("),
    global_events_connected:
      hook.includes('window.addEventListener(\n      "keydown"') &&
      hook.includes('window.addEventListener(\n      "keyup"') &&
      hook.includes('window.removeEventListener(\n        "keydown"') &&
      hook.includes('window.removeEventListener(\n        "keyup"'),
    browser_default_controlled:
      hook.includes("if (result.preventDefault)") &&
      hook.includes("event.preventDefault()") &&
      hook.includes("if (result.handled && result.intent)"),
    authoritative_context_mapped:
      hook.includes("view.timeline.revision") &&
      hook.includes("view.timeline.playheadTime") &&
      hook.includes("view.timeline.clipboard.selectedClipIds") &&
      hook.includes("view.timeline.commandTarget?.clipId") &&
      hook.includes("view.header.canUndo") &&
      hook.includes("view.header.canRedo"),
    platform_modifiers_supported:
      hook.includes("navigator.platform.toLowerCase()") &&
      hook.includes('return "macos"') &&
      hook.includes('return "linux"') &&
      hook.includes('return "windows"'),
    editable_target_forwarded:
      hook.includes("target.isContentEditable") &&
      hook.includes('target.getAttribute("role")') &&
      hook.includes("tagName: target.tagName"),
    undo_redo_delegated_once:
      hook.match(/onUndo\(\);/g)?.length === 1 &&
      hook.match(/onRedo\(\);/g)?.length === 1,
    edit_commands_delegated:
      hook.includes('case "split_clip":') &&
      hook.includes('case "duplicate_clip":') &&
      hook.includes('case "delete_clip":') &&
      hook.match(/onTimelineCommand\(\{/g)?.length === 5,
    clipboard_commands_delegated:
      hook.includes('case "copy":') &&
      hook.includes('case "cut":') &&
      hook.includes('case "paste":') &&
      hook.match(/onClipboardCommand\(\{/g)?.length === 3,
    exactly_one_intent_boundary:
      hook.match(/executeIntent\(result\.intent\)/g)?.length === 1,
    runtime_revision_authoritative:
      !hook.includes("expected_revision") &&
      !hook.includes("expectedRevision"),
    workspace_connects_keyboard_boundary:
      workspace.includes("useReviewRuntimeKeyboardEditing") &&
      workspace.includes("onUndo,") &&
      workspace.includes("onRedo,") &&
      workspace.includes("onTimelineCommand,") &&
      workspace.includes("onClipboardCommand,"),
    busy_state_is_atomic:
      workspace.includes("clipDrag.drag.active") &&
      workspace.includes("clipTrim.trim.active") &&
      workspace.includes("commandPending ||") &&
      workspace.includes("clipboardPending ||") &&
      hook.includes("busy: disabled"),
    shell_status_forwarded:
      workspace.includes("keyboard={keyboard}") &&
      shell.includes("data-review-keyboard-controls") &&
      shell.includes("data-review-keyboard-operation"),
    runtime_disposed_on_unmount:
      hook.includes("runtime.dispose()") &&
      hook.includes("return runtime.subscribe("),
    no_optimistic_timeline_state:
      !hook.includes("setTimeline") &&
      !hook.includes("setSnapshot") &&
      !shell.includes("setTimeline") &&
      !shell.includes("setSnapshot"),
    no_direct_api_calls:
      !hook.includes("fetch(") &&
      !hook.includes("/api/") &&
      !shell.includes("fetch("),
    no_direct_timeline_mutation:
      !hook.includes("timeline.tracks =") &&
      !hook.includes("split_clip(") &&
      !hook.includes("duplicate_clip(") &&
      !hook.includes("delete_clip("),
  };

  console.log(
    "=== Runtime-connected Keyboard Editing Controls ===",
  );
  for (const [name, value] of Object.entries(checks)) {
    console.log(`${name}: ${value}`);
    assert.equal(value, true, `${name} failed`);
  }
  console.log(
    "\nDONE: Runtime-connected keyboard editing controls test completed.",
  );
}

main();
