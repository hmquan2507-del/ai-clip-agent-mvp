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
const hookSource = fs.readFileSync(
  hookPath,
  "utf8",
);
const timelineSource = fs.readFileSync(
  timelinePath,
  "utf8",
);

const {
  REVIEW_TIMELINE_TRACK_COMPATIBILITY_VERSION,
  createReviewTimelineDragSessionRuntime,
  evaluateReviewTimelineTrackCompatibility,
} = require(dragIndexPath);

const viewport = {
  left: 0,
  top: 0,
  width: 1000,
  height: 160,
  scrollLeft: 0,
  contentWidth: 1000,
};
const lanes = [
  {
    trackId: "video-primary",
    trackType: "video_primary",
    top: 0,
    height: 40,
    locked: false,
  },
  {
    trackId: "video-overlay",
    trackType: "video_overlay",
    top: 40,
    height: 40,
    locked: false,
  },
  {
    trackId: "subtitle",
    trackType: "subtitle",
    top: 80,
    height: 40,
    locked: false,
  },
  {
    trackId: "locked-overlay",
    trackType: "video_overlay",
    top: 120,
    height: 40,
    locked: true,
  },
];
const environment = {
  viewport,
  timelineDuration: 20,
  fps: 30,
  lanes,
  quantizeToFrame: false,
  snap: {
    thresholdPixels: 8,
    clips: [
      {
        clipId: "overlay-neighbor",
        trackId: "video-overlay",
        startTime: 6,
        endTime: 8,
      },
      {
        clipId: "primary-neighbor",
        trackId: "video-primary",
        startTime: 5.9,
        endTime: 7.9,
      },
    ],
    includeFrames: false,
    includePlayhead: false,
  },
};

function createRuntime(id) {
  const runtime =
    createReviewTimelineDragSessionRuntime({
      dragThreshold: 0,
      createSessionId: () => id,
    });
  runtime.arm({
    productionId: "production-1",
    timelineRevision: 12,
    source: {
      clipId: "video-clip",
      clipType: "video",
      trackId: "video-primary",
      startTime: 2,
      endTime: 4,
      duration: 2,
    },
    pointer: {
      clientX: 100,
      clientY: 20,
    },
    environment,
  });
  return runtime;
}

function main() {
  const inputBefore = structuredClone({
    viewport,
    lanes,
    environment,
  });

  const compatible =
    evaluateReviewTimelineTrackCompatibility(
      "video",
      "video_overlay",
    );
  const incompatible =
    evaluateReviewTimelineTrackCompatibility(
      "video",
      "subtitle",
    );

  const validRuntime = createRuntime(
    "drag-valid",
  );
  const validState = validRuntime.move({
    pointer: {
      clientX: 300,
      clientY: 60,
    },
  });
  const validIntent =
    validRuntime.prepareCommit();

  const invalidRuntime = createRuntime(
    "drag-invalid",
  );
  const invalidState = invalidRuntime.move({
    pointer: {
      clientX: 300,
      clientY: 100,
    },
  });
  let invalidCommitBlocked = false;
  try {
    invalidRuntime.prepareCommit();
  } catch {
    invalidCommitBlocked = true;
  }

  const lockedRuntime = createRuntime(
    "drag-locked",
  );
  const lockedState = lockedRuntime.move({
    pointer: {
      clientX: 300,
      clientY: 140,
    },
  });

  const checks = {
    compatibility_version_valid:
      REVIEW_TIMELINE_TRACK_COMPATIBILITY_VERSION ===
        "16.5.5" &&
      compatible.version === "16.5.5",
    compatible_track_allowed:
      compatible.compatible === true,
    incompatible_track_rejected:
      incompatible.compatible === false &&
      incompatible.reason ===
        "incompatible_clip_type",
    cross_track_projection_valid:
      validState.projection.valid === true &&
      validState.projection.targetTrackId ===
        "video-overlay",
    cross_track_intent_valid:
      validIntent.clipId === "video-clip" &&
      validIntent.targetTrackId ===
        "video-overlay" &&
      !("expected_revision" in validIntent),
    target_track_snap_authoritative:
      validState.snapResult?.candidate
        ?.targetId ===
        "overlay-neighbor:start" &&
      validState.snapResult?.candidate
        ?.targetId !==
        "primary-neighbor:start",
    incompatible_projection_blocked:
      invalidState.projection.valid === false &&
      invalidState.projection.blockedReason ===
        "incompatible_track" &&
      invalidCommitBlocked,
    locked_target_blocked:
      lockedState.projection.valid === false &&
      lockedState.projection.blockedReason ===
        "track_locked",
    all_lanes_forwarded:
      hookSource.includes(
        "lanes: geometry.lanes",
      ) &&
      !hookSource.includes(
        "geometry.lanes.filter(",
      ),
    clip_type_forwarded:
      hookSource.includes(
        "clipType:",
      ),
    ghost_preview_rendered:
      timelineSource.includes(
        'data-review-cross-track-ghost="true"',
      ) &&
      timelineSource.includes(
        "crossTrackDrag",
      ),
    target_lane_feedback_rendered:
      timelineSource.includes(
        "data-drag-target",
      ) &&
      timelineSource.includes(
        '"blocked"',
      ),
    pointer_capture_source_preserved:
      timelineSource.includes(
        "setPointerCapture",
      ) &&
      timelineSource.includes(
        '"opacity-0"',
      ),
    inputs_unchanged:
      JSON.stringify({
        viewport,
        lanes,
        environment,
      }) === JSON.stringify(inputBefore),
    no_direct_api_or_mutation:
      !hookSource.includes("fetch(") &&
      !timelineSource.includes("fetch(") &&
      !hookSource.includes("expected_revision") &&
      !timelineSource.includes("start_time ="),
  };

  console.log(
    "=== Cross-track Drag & Drop ===",
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
    "\nDONE: Cross-track drag and drop test completed.",
  );
}

main();
