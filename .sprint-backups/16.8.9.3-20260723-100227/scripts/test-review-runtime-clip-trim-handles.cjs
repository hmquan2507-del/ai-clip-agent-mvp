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
  const contracts = read(
    "src/features/review/integration/contracts.ts",
  );
  const hook = read(
    "src/features/review/integration/use-runtime-clip-trim.ts",
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
  const timeline = read(
    "src/features/review/shell/timeline.tsx",
  );

  const checks = {
    trim_view_contract_valid:
      contracts.includes("ReviewTimelineClipTrimStartIntent") &&
      contracts.includes("ReviewTimelineClipTrimMoveIntent") &&
      contracts.includes("ReviewTimelineClipTrimView"),
    runtime_hook_owns_trim_session:
      hook.includes("createReviewTimelineTrimSessionRuntime") &&
      hook.includes("runtime.prepareCommit()") &&
      hook.includes("runtime.completeCommit()") &&
      hook.includes("runtime.failCommit("),
    backend_selection_authoritative:
      hook.includes("context.clip.selected") &&
      !hook.includes("setSelected") &&
      !timeline.includes("setSelected"),
    authoritative_geometry_used:
      hook.includes("context.clip.startTime") &&
      hook.includes("context.clip.endTime") &&
      hook.includes("context.clip.duration") &&
      hook.includes("view.timeline.revision"),
    frame_quantized_environment:
      hook.includes("quantizeToFrame: true") &&
      hook.includes("minimumDuration:"),
    both_trim_commands_delegated:
      hook.includes("await trimClipStart({") &&
      hook.includes("await trimClipEnd({") &&
      hook.includes('intent.operation === "trim_clip_start"'),
    exactly_one_command_boundary:
      hook.match(/runtime\.prepareCommit\(\)/g)?.length === 1 &&
      hook.match(/await trimClipStart\(\{/g)?.length === 1 &&
      hook.match(/await trimClipEnd\(\{/g)?.length === 1,
    expected_revision_owned_by_runtime:
      !hook.includes("expected_revision") &&
      !timeline.includes("expected_revision"),
    workspace_connects_action_boundary:
      workspace.includes("useReviewRuntimeClipTrim") &&
      workspace.includes("actions.trimClipStart") &&
      workspace.includes("actions.trimClipEnd"),
    integration_exported:
      integrationIndex.includes('export * from "./use-runtime-clip-trim"'),
    shell_forwards_trim_contract:
      shell.includes("trim={trim}") &&
      shell.includes("onClipTrimStart") &&
      shell.includes("onClipTrimMove") &&
      shell.includes("onClipTrimDrop") &&
      shell.includes("onClipTrimCancel"),
    selected_clip_handles_rendered:
      timeline.includes('data-review-trim-handle="start"') &&
      timeline.includes('data-review-trim-handle="end"') &&
      timeline.includes("clip.selected") &&
      timeline.includes("!track.locked"),
    pointer_events_complete:
      timeline.includes("beginClipTrim(") &&
      timeline.includes("moveClipTrim") &&
      timeline.includes("dropClipTrim") &&
      timeline.includes("cancelClipTrim"),
    escape_cancel_connected:
      timeline.includes('event.key === "Escape"') &&
      timeline.includes('"escape_pressed"') &&
      timeline.includes("releasePointerCapture"),
    preview_uses_runtime_projection:
      /trimProjection\s*\.projectedStartTime/.test(timeline) &&
      /trimProjection\s*\.projectedDuration/.test(timeline) &&
      timeline.includes("projectedWidth"),
    pending_state_visible:
      timeline.includes("trim?.trimming") &&
      timeline.includes("trim?.committing") &&
      timeline.includes("data-review-trim-failure"),
    interactions_disabled_atomically:
      timeline.includes("Boolean(trim?.active)") &&
      timeline.includes("drag?.active ||") &&
      workspace.includes("clipDrag.drag.active"),
    conflict_recovery_connected:
      hook.includes("ReviewWorkspaceAPIError") &&
      hook.includes("error.isRevisionConflict") &&
      timeline.includes("Đã đồng bộ bản mới"),
    no_optimistic_timeline_state:
      !hook.includes("setTimeline") &&
      !hook.includes("setSnapshot") &&
      !timeline.includes("setTimeline") &&
      !timeline.includes("setSnapshot"),
    no_direct_api_calls:
      !hook.includes("fetch(") &&
      !timeline.includes("fetch(") &&
      !shell.includes("/api/"),
    no_direct_timeline_mutation:
      !hook.includes("timeline.tracks =") &&
      !timeline.includes("timeline.tracks =") &&
      !timeline.includes("trim_clip_start(") &&
      !timeline.includes("trim_clip_end("),
  };

  console.log("=== Runtime-connected Clip Trim Handles ===");
  for (const [name, value] of Object.entries(checks)) {
    console.log(`${name}: ${value}`);
    assert.equal(value, true, `${name} failed`);
  }
  console.log(
    "\nDONE: Runtime-connected clip trim handles test completed.",
  );
}

main();
