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
const snapRuntimePath = path.resolve(
  __dirname,
  "../src/features/review/drag/snap-runtime.ts",
);
const snapSource = fs.readFileSync(
  snapRuntimePath,
  "utf8",
);

const {
  REVIEW_TIMELINE_SNAP_CONTRACT_VERSION,
  createReviewTimelineDragSessionRuntime,
  createReviewTimelineSnapRuntime,
} = require(dragIndexPath);

const viewport = {
  left: 0,
  top: 0,
  width: 500,
  height: 100,
  scrollLeft: 0,
  contentWidth: 1000,
};
const baseContext = {
  thresholdPixels: 8,
  playheadTime: 5,
  clips: [
    {
      clipId: "source",
      trackId: "video-1",
      startTime: 2,
      endTime: 4,
    },
    {
      clipId: "neighbor",
      trackId: "video-1",
      startTime: 3,
      endTime: 5,
    },
    {
      clipId: "other-track",
      trackId: "video-2",
      startTime: 4.92,
      endTime: 6.92,
    },
  ],
};
const baseInput = {
  sourceClipId: "source",
  targetTrackId: "video-1",
  projectedStartTime: 4.91,
  clipDuration: 2,
  timelineDuration: 20,
  fps: 10,
  viewport,
  context: baseContext,
};

function main() {
  const runtime =
    createReviewTimelineSnapRuntime();
  const inputBefore = structuredClone(
    baseInput,
  );

  const frame = runtime.project({
    ...baseInput,
    projectedStartTime: 4.94,
    context: {
      ...baseContext,
      includePlayhead: false,
      includeClipEdges: false,
    },
  });
  const playhead = runtime.project({
    ...baseInput,
    context: {
      ...baseContext,
      includeFrames: false,
      includeClipEdges: false,
    },
  });
  const clipEdge = runtime.project({
    ...baseInput,
    context: {
      ...baseContext,
      includeFrames: false,
      includePlayhead: false,
    },
  });
  const tie = runtime.project({
    ...baseInput,
    context: {
      ...baseContext,
      includeFrames: false,
    },
  });
  const endAlignment = runtime.project({
    ...baseInput,
    projectedStartTime: 3.09,
    context: {
      ...baseContext,
      clips: [
        baseContext.clips[0],
        {
          clipId: "end-target",
          trackId: "video-1",
          startTime: 1,
          endTime: 5,
        },
      ],
      includeFrames: false,
      includePlayhead: false,
    },
  });
  const outsideThreshold = runtime.project({
    ...baseInput,
    projectedStartTime: 4.7,
    context: {
      ...baseContext,
      includeFrames: false,
      includePlayhead: false,
    },
  });
  const sourceExcluded = runtime.project({
    ...baseInput,
    context: {
      thresholdPixels: 20,
      clips: [baseContext.clips[0]],
      includeFrames: false,
      includePlayhead: false,
    },
  });
  const disabled = runtime.project({
    ...baseInput,
    context: {
      ...baseContext,
      enabled: false,
    },
  });

  const isolated = runtime.project(
    baseInput,
  );
  if (isolated.candidate) {
    isolated.candidate.targetId =
      "changed-outside";
  }
  const repeated = runtime.project(
    baseInput,
  );

  const dragRuntime =
    createReviewTimelineDragSessionRuntime({
      dragThreshold: 0,
      createSessionId: () => "drag-snap",
    });
  dragRuntime.arm({
    productionId: "production-1",
    timelineRevision: 9,
    source: {
      clipId: "source",
      trackId: "video-1",
      startTime: 2,
      endTime: 4,
      duration: 2,
    },
    pointer: {
      clientX: 100,
      clientY: 40,
    },
    environment: {
      viewport,
      timelineDuration: 20,
      fps: 10,
      quantizeToFrame: false,
      lanes: [
        {
          trackId: "video-1",
          top: 0,
          height: 100,
          locked: false,
        },
      ],
      snap: {
        thresholdPixels: 8,
        clips: baseContext.clips,
        includeFrames: false,
        includePlayhead: false,
      },
    },
  });
  const dragState = dragRuntime.move({
    pointer: {
      clientX: 245,
      clientY: 40,
    },
  });
  const dragIntent =
    dragRuntime.prepareCommit();

  const checks = {
    contract_version_valid:
      REVIEW_TIMELINE_SNAP_CONTRACT_VERSION ===
        "16.5.3" &&
      frame.contractVersion === "16.5.3",
    pixel_threshold_converted:
      approximately(
        clipEdge.thresholdTime,
        0.16,
      ),
    frame_snap_valid:
      frame.snapped &&
      frame.candidate.targetType === "frame" &&
      approximately(
        frame.snappedStartTime,
        4.9,
      ),
    playhead_snap_valid:
      playhead.snapped &&
      playhead.candidate.targetType ===
        "playhead" &&
      approximately(
        playhead.snappedStartTime,
        5,
      ),
    clip_edge_snap_valid:
      clipEdge.snapped &&
      clipEdge.candidate.targetType ===
        "clip_end" &&
      clipEdge.candidate.targetId ===
        "neighbor:end",
    end_alignment_valid:
      endAlignment.snapped &&
      endAlignment.candidate.alignment ===
        "end" &&
      approximately(
        endAlignment.snappedStartTime,
        3,
      ),
    deterministic_tie_break:
      tie.candidate.targetType ===
        "clip_end",
    source_clip_excluded:
      !sourceExcluded.snapped &&
      sourceExcluded.consideredCandidateCount ===
        0,
    other_track_excluded:
      clipEdge.candidate.targetId !==
        "other-track:start",
    outside_threshold_unsnapped:
      !outsideThreshold.snapped &&
      approximately(
        outsideThreshold.snappedStartTime,
        4.7,
      ),
    disabled_is_read_only:
      !disabled.snapped &&
      approximately(
        disabled.snappedStartTime,
        4.91,
      ),
    result_isolated:
      repeated.candidate?.targetId !==
        "changed-outside",
    inputs_unchanged:
      JSON.stringify(baseInput) ===
        JSON.stringify(inputBefore),
    drag_projection_snapped:
      dragState.snapResult?.snapped === true &&
      approximately(
        dragState.projection.projectedStartTime,
        5,
      ),
    commit_uses_snapped_projection:
      approximately(
        dragIntent.newStartTime,
        5,
      ) &&
      !("expected_revision" in dragIntent),
    no_api_or_timeline_mutation:
      !snapSource.includes("fetch(") &&
      !snapSource.includes("../api") &&
      !snapSource.includes("moveClip(") &&
      !snapSource.includes("expected_revision"),
  };

  console.log(
    "=== Timeline Snap Runtime ===",
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
    "\nDONE: Timeline snap runtime test completed.",
  );
}

function approximately(
  left,
  right,
  epsilon = 0.000001,
) {
  return Math.abs(left - right) <= epsilon;
}

main();
