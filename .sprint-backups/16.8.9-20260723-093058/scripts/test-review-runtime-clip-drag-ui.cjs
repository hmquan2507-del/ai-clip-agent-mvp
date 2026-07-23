/* eslint-disable @typescript-eslint/no-require-imports */

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

function read(relativePath) {
  return fs.readFileSync(
    path.resolve(
      __dirname,
      "..",
      relativePath,
    ),
    "utf8",
  );
}

function main() {
  const hook = read(
    "src/features/review/integration/use-runtime-clip-drag.ts",
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
  const contracts = read(
    "src/features/review/integration/contracts.ts",
  );
  const adapters = read(
    "src/features/review/integration/adapters.ts",
  );

  const checks = {
    drag_view_contract_valid:
      contracts.includes(
        "ReviewTimelineClipDragView",
      ) &&
      contracts.includes(
        "ReviewTimelineClipDragStartIntent",
      ) &&
      contracts.includes(
        "ReviewTimelineClipDragMoveIntent",
      ),
    authoritative_geometry_available:
      contracts.includes("startTime: number") &&
      contracts.includes("endTime: number") &&
      contracts.includes("duration: number") &&
      contracts.includes("revision: number") &&
      adapters.includes("timeline.revision") &&
      adapters.includes("clip.start_time"),
    runtime_hook_owns_drag_session:
      hook.includes(
        "createReviewTimelineDragSessionRuntime",
      ) &&
      hook.includes("runtime.arm({") &&
      hook.includes("runtime.move({") &&
      hook.includes("runtime.prepareCommit()"),
    lane_geometry_runtime_owned:
      hook.includes("lanes: geometry.lanes") &&
      hook.includes("sourceTrackId"),
    snap_context_connected:
      hook.includes("thresholdPixels: 8") &&
      hook.includes("playheadTime:") &&
      hook.includes("view.timeline.tracks.flatMap("),
    drop_delegates_once:
      count(hook, "await moveClip({") === 1 &&
      hook.includes("runtime.completeCommit()"),
    expected_revision_owned_by_runtime:
      !hook.includes("expected_revision"),
    workspace_connects_action_boundary:
      workspace.includes(
        "useReviewRuntimeClipDrag",
      ) &&
      workspace.includes(
        "moveClip: actions.moveClip",
      ) &&
      workspace.includes(
        "onClipDragStart={clipDrag.begin}",
      ),
    shell_forwards_drag_contract:
      shell.includes("drag={drag}") &&
      shell.includes("onClipDragMove") &&
      shell.includes("onClipDragDrop") &&
      shell.includes("onClipDragCancel"),
    pointer_events_complete:
      timeline.includes("onPointerDown") &&
      timeline.includes("onPointerMove") &&
      timeline.includes("onPointerUp") &&
      timeline.includes("onPointerCancel") &&
      timeline.includes("setPointerCapture"),
    escape_cancel_connected:
      timeline.includes(
        'event.key ===\n                            "Escape"',
      ) &&
      timeline.includes('"escape_pressed"'),
    click_after_drag_suppressed:
      timeline.includes("suppressClickRef") &&
      timeline.includes("event.stopPropagation()"),
    preview_uses_runtime_projection:
      timeline.includes("projectedStartTime") &&
      timeline.includes("data-drag-phase"),
    snap_guide_rendered:
      timeline.includes(
        'data-review-snap-guide="true"',
      ) &&
      timeline.includes("candidate") &&
      timeline.includes("targetTime"),
    pending_state_visible:
      timeline.includes("Đang kéo clip…") &&
      timeline.includes(
        "Đang áp dụng vị trí…",
      ),
    locked_clip_read_only:
      hook.includes("context.track.locked") &&
      timeline.includes("clip.editable") &&
      timeline.includes("Track đang khóa"),
    no_direct_api_calls:
      !hook.includes("fetch(") &&
      !timeline.includes("fetch(") &&
      !shell.includes("/api/"),
    no_direct_timeline_mutation:
      !timeline.includes("start_time =") &&
      !hook.includes("start_time =") &&
      !timeline.includes("timeline.tracks.push") &&
      !hook.includes("timeline.tracks.push"),
  };

  console.log(
    "=== Runtime-connected Clip Drag UI ===",
  );
  for (const [key, value] of
    Object.entries(checks)) {
    console.log(`${key}: ${value}`);
  }

  assert.equal(
    Object.values(checks).every(Boolean),
    true,
    JSON.stringify(checks, null, 2),
  );

  console.log(
    "\nDONE: Runtime-connected clip drag UI test completed.",
  );
}

function count(source, value) {
  return source.split(value).length - 1;
}

main();
