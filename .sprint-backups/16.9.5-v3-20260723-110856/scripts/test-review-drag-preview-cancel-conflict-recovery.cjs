/* eslint-disable @typescript-eslint/no-require-imports */

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const ts = require("typescript");

require.extensions[".ts"] =
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
          target: ts.ScriptTarget.ES2022,
          module: ts.ModuleKind.CommonJS,
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

const dragIndexPath = path.resolve(
  __dirname,
  "../src/features/review/drag/index.ts",
);
const hookPath = path.resolve(
  __dirname,
  "../src/features/review/integration/use-runtime-clip-drag.ts",
);
const timelinePath = path.resolve(
  __dirname,
  "../src/features/review/shell/timeline.tsx",
);
const stateRuntimePath = path.resolve(
  __dirname,
  "../src/features/review/state/runtime.ts",
);

const hookSource = fs.readFileSync(
  hookPath,
  "utf8",
);
const timelineSource = fs.readFileSync(
  timelinePath,
  "utf8",
);
const stateRuntimeSource = fs.readFileSync(
  stateRuntimePath,
  "utf8",
);

const {
  createReviewTimelineDragSessionRuntime,
} = require(dragIndexPath);

const environment = {
  viewport: {
    left: 0,
    top: 0,
    width: 1000,
    height: 40,
    scrollLeft: 0,
    contentWidth: 1000,
  },
  timelineDuration: 20,
  fps: 30,
  lanes: [
    {
      trackId: "video-1",
      trackType: "video_primary",
      top: 0,
      height: 40,
      locked: false,
    },
  ],
  quantizeToFrame: false,
};
const source = {
  clipId: "clip-1",
  clipType: "video",
  trackId: "video-1",
  startTime: 2,
  endTime: 4,
  duration: 2,
};

function arm(runtime, revision = 5) {
  runtime.arm({
    productionId: "production-1",
    timelineRevision: revision,
    source,
    pointer: {
      clientX: 100,
      clientY: 20,
    },
    environment,
  });
  runtime.move({
    pointer: {
      clientX: 250,
      clientY: 20,
    },
  });
}

function main() {
  const runtime =
    createReviewTimelineDragSessionRuntime({
      dragThreshold: 0,
      createSessionId: () => "drag-failure",
      now: () =>
        "2026-07-18T10:00:00.000Z",
    });
  arm(runtime);
  const preview = runtime.getState();
  const intent = runtime.prepareCommit();
  const failed = runtime.failCommit({
    code: "revision_conflict",
    message:
      "Timeline revision changed.",
    technicalMessage:
      "Expected 5, received 6.",
    isRevisionConflict: true,
    expectedRevision: 5,
    currentRevision: 6,
  });

  const isolatedFailure = failed.failure;
  isolatedFailure.message =
    "changed-outside";

  const afterIsolation = runtime.getState();
  const rearmed = runtime.arm({
    productionId: "production-1",
    timelineRevision: 6,
    source,
    pointer: {
      clientX: 100,
      clientY: 20,
    },
    environment,
  });
  const cancelled = runtime.cancel(
    "escape_pressed",
  );

  const invalidRuntime =
    createReviewTimelineDragSessionRuntime({
      dragThreshold: 0,
      createSessionId: () => "drag-invalid",
    });
  invalidRuntime.arm({
    productionId: "production-1",
    timelineRevision: 6,
    source,
    pointer: {
      clientX: 100,
      clientY: 20,
    },
    environment,
  });
  invalidRuntime.move({
    pointer: {
      clientX: 250,
      clientY: 100,
    },
  });
  const invalidCancelled =
    invalidRuntime.cancel(
      "invalid_drop",
    );

  const checks = {
    preview_is_temporary:
      preview.phase === "dragging" &&
      preview.projection.projectedStartTime !==
        source.startTime &&
      source.startTime === 2,
    commit_intent_created_once:
      intent.clipId === "clip-1" &&
      runtime.getState().commitIntent === null,
    failure_state_valid:
      failed.phase === "failed" &&
      failed.session.phase === "failed" &&
      failed.failure.code ===
        "revision_conflict" &&
      failed.failure.isRevisionConflict &&
      failed.failure.expectedRevision === 5 &&
      failed.failure.currentRevision === 6,
    failed_preview_rolls_back:
      hookSource.includes(
        'dragState.phase === "armed"',
      ) &&
      hookSource.includes(
        'dragState.phase === "committing"',
      ) &&
      !hookSource.includes(
        'dragState.phase !== "failed"',
      ),
    failure_snapshot_isolated:
      afterIsolation.failure.message ===
        "Timeline revision changed.",
    next_drag_uses_new_revision:
      rearmed.phase === "armed" &&
      rearmed.session.timelineRevision === 6 &&
      rearmed.failure === null,
    escape_cancel_valid:
      cancelled.phase === "cancelled" &&
      cancelled.cancelReason ===
        "escape_pressed" &&
      cancelled.commitIntent === null,
    invalid_drop_cancel_valid:
      invalidCancelled.phase ===
        "cancelled" &&
      invalidCancelled.cancelReason ===
        "invalid_drop",
    workspace_change_cancel_connected:
      hookSource.includes(
        '"workspace_changed"',
      ) &&
      hookSource.includes(
        "session.timelineRevision !==",
      ),
    revision_conflict_normalized:
      hookSource.includes(
        "error.isRevisionConflict",
      ) &&
      hookSource.includes(
        '"revision_conflict"',
      ) &&
      hookSource.includes(
        "runtime.failCommit(",
      ),
    authoritative_recovery_reused:
      stateRuntimeSource.includes(
        "recoverRevisionConflict(",
      ) &&
      stateRuntimeSource.includes(
        "await this.client.getSnapshot(",
      ) &&
      !hookSource.includes("getSnapshot(") &&
      !hookSource.includes("refresh("),
    conflict_feedback_visible:
      timelineSource.includes(
        'data-review-drag-failure=',
      ) &&
      timelineSource.includes(
        "Đã đồng bộ bản mới",
      ),
    escape_releases_pointer_capture:
      timelineSource.includes(
        "releasePointerCapture",
      ) &&
      timelineSource.includes(
        '"escape_pressed"',
      ),
    no_retry_or_duplicate_command:
      count(hookSource, "await moveClip({") === 1 &&
      !hookSource.includes("retryMoveClip") &&
      !hookSource.includes("expected_revision"),
    no_direct_timeline_mutation:
      !hookSource.includes("start_time =") &&
      !timelineSource.includes("start_time ="),
  };

  console.log(
    "=== Drag Preview, Cancel & Conflict Recovery ===",
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
    "\nDONE: Drag preview, cancel and conflict recovery test completed.",
  );
}

function count(sourceText, value) {
  return sourceText.split(value).length - 1;
}

main();
