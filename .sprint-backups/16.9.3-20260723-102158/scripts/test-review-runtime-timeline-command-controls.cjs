/* eslint-disable @typescript-eslint/no-require-imports */

const assert =
  require("node:assert/strict");

const fs =
  require("node:fs");

const path =
  require("node:path");

const root = path.resolve(
  __dirname,
  "../src/features/review",
);

function read(relativePath) {
  return fs.readFileSync(
    path.resolve(
      root,
      relativePath,
    ),
    "utf8",
  );
}

function includesAll(
  source,
  values,
) {
  return values.every(
    (value) =>
      source.includes(value),
  );
}

function main() {
  const adapters =
    read(
      "integration/adapters.ts",
    );

  const contracts =
    read(
      "integration/contracts.ts",
    );

  const runtimeWorkspace =
    read(
      "integration/runtime-workspace.tsx",
    );

  const shell =
    read(
      "shell/review-editor-shell.tsx",
    );

  const topbar =
    read(
      "shell/editor-topbar.tsx",
    );

  const timeline =
    read(
      "shell/timeline.tsx",
    );

  const checks = {
    command_intents_complete:
      includesAll(
        contracts,
        [
          '"split_clip"',
          '"duplicate_clip"',
          '"delete_clip"',
          '"close_gap"',
          "ReviewTimelineCommandIntent",
        ],
      ),

    command_target_derived:
      includesAll(
        adapters,
        [
          "buildCommandTarget(",
          "findGapBeforeClip(",
          "minimum_clip_duration",
          "selection.cursor_time",
          "track.locked",
        ],
      ),

    split_time_safe:
      includesAll(
        adapters,
        [
          "minimumSplitTime",
          "maximumSplitTime",
          "clip.duration / 2",
        ],
      ),

    locked_track_read_only:
      adapters.includes(
        "editable:",
      ) &&
      adapters.includes(
        "!track.locked",
      ),

    gap_context_derived:
      includesAll(
        adapters,
        [
          "gapBefore:",
          "trackId:",
          "startTime:",
          "endTime:",
        ],
      ),

    runtime_commands_delegated:
      includesAll(
        runtimeWorkspace,
        [
          "actions.splitClip({",
          "actions.duplicateClip({",
          "actions.deleteClip({",
          "actions.closeGap({",
        ],
      ),

    undo_redo_delegated:
      includesAll(
        runtimeWorkspace,
        [
          "actions.undoTimeline()",
          "actions.redoTimeline()",
          "onUndo={undoTimeline}",
          "onRedo={redoTimeline}",
        ],
      ),

    expected_revision_owned_by_runtime:
      !runtimeWorkspace.includes(
        "expected_revision",
      ) &&
      !timeline.includes(
        "expected_revision",
      ),

    shell_forwards_commands:
      includesAll(
        shell,
        [
          "onTimelineCommand?:",
          "onTimelineCommand={",
          "onUndo={onUndo}",
          "onRedo={onRedo}",
          "pendingCommand={",
        ],
      ),

    topbar_undo_connected:
      includesAll(
        topbar,
        [
          "onUndo?: () => void",
          "onClick={onUndo}",
          "!view?.canUndo",
        ],
      ),

    topbar_redo_connected:
      includesAll(
        topbar,
        [
          "onRedo?: () => void",
          "onClick={onRedo}",
          "!view?.canRedo",
        ],
      ),

    timeline_controls_complete:
      includesAll(
        timeline,
        [
          "splitSelectedClip",
          "duplicateSelectedClip",
          "deleteSelectedClip",
          "closeGapBeforeClip",
        ],
      ),

    command_pending_visible:
      includesAll(
        timeline,
        [
          "commandPending",
          "commandLabel(",
          "Đang tách clip…",
          "Đang xóa clip…",
        ],
      ),

    command_controls_disabled_atomically:
      includesAll(
        timeline,
        [
          "controlsDisabled",
          "canEditTarget",
          "disabled={!canSplit}",
          "disabled={",
        ],
      ),

    no_direct_api_calls:
      !runtimeWorkspace.includes(
        "/timeline/",
      ) &&
      !timeline.includes(
        "fetch(",
      ) &&
      !topbar.includes(
        "fetch(",
      ),

    no_direct_timeline_mutation:
      !timeline.includes(
        "timeline.revision++",
      ) &&
      !timeline.includes(
        "tracks.splice",
      ) &&
      !timeline.includes(
        "clips.splice",
      ) &&
      !runtimeWorkspace.includes(
        "snapshot.timeline =",
      ),
  };

  console.log(
    "=== Runtime-connected Timeline Command Controls ===",
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
    "\nDONE: Runtime-connected Timeline Command Controls test completed.",
  );
}

main();