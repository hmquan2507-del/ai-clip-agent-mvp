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
  const stateRuntime =
    read("state/runtime.ts");

  const reactContracts =
    read("react/contracts.ts");

  const provider =
    read("react/provider.tsx");

  const hooks =
    read("react/hooks.ts");

  const adapters =
    read("integration/adapters.ts");

  const integrationContracts =
    read("integration/contracts.ts");

  const runtimeWorkspace =
    read(
      "integration/runtime-workspace.tsx",
    );

  const shell =
    read(
      "shell/review-editor-shell.tsx",
    );

  const timeline =
    read("shell/timeline.tsx");

  const checks = {
    selection_runtime_available:
      includesAll(
        stateRuntime,
        [
          "async selectClip(",
          "validateSelectionResponse(",
          '"selecting"',
          '"select"',
        ],
      ),

    provider_action_contract_valid:
      includesAll(
        reactContracts,
        [
          "ReviewTimelineSelectionActions",
          "selectClip(",
          "SelectTimelineClipInput",
          "selecting: boolean",
        ],
      ),

    provider_delegates_to_runtime:
      includesAll(
        provider,
        [
          "const selectClip = useCallback(",
          "runtime.selectClip(",
          "selectClip,",
        ],
      ),

    selection_hook_available:
      includesAll(
        hooks,
        [
          "useReviewTimelineSelectionActions",
          "ReviewTimelineSelectionActions",
          'status === "selecting"',
        ],
      ),

    selection_intent_contract_valid:
      includesAll(
        integrationContracts,
        [
          "ReviewTimelineSelectionIntent",
          "clipId: string",
          "additive: boolean",
          "moveCursor: boolean",
        ],
      ),

    runtime_workspace_delegates:
      includesAll(
        runtimeWorkspace,
        [
          "actions.selectClip({",
          "clip_id:",
          "additive:",
          "move_cursor:",
          "onSelectClip={selectClip}",
        ],
      ),

    failed_selection_keeps_workspace:
      runtimeWorkspace.includes(
        "if (!state.snapshot)",
      ) &&
      !runtimeWorkspace.includes(
        'state.status === "error" || !state.snapshot',
      ),

    shell_forwards_selection:
      includesAll(
        shell,
        [
          "onSelectClip?:",
          "selecting?: boolean",
          "onSelectClip={onSelectClip}",
          "selecting={selecting}",
        ],
      ),

    timeline_click_connected:
      includesAll(
        timeline,
        [
          "handleClipClick(",
          "onSelectClip({",
          "clipId,",
          "onClick={",
        ],
      ),

    additive_modifier_supported:
      includesAll(
        timeline,
        [
          "event.ctrlKey",
          "event.metaKey",
          "additive,",
        ],
      ),

    move_cursor_forwarded:
      timeline.includes(
        "moveCursor: true",
      ),

    pending_selection_visible:
    includesAll(
    timeline,
    [
      "aria-busy={",
      "selecting ||",
      "Đang chọn clip…",
      "disabled={",
      "selecting",
    ],
  ),
backend_selection_authoritative:
  includesAll(
    adapters,
    [
      "snapshot.selection.state",
      "selection.selected_clip_ids",
      "selection.active_clip_id",
      "selectedIds.has(",
      "clip.clip_id",
    ],
  ) &&
  timeline.includes(
    "aria-pressed={",
  ) &&
  timeline.includes(
    "clip.selected",
  ),

    no_optimistic_selection_state:
      !timeline.includes(
        "useState(",
      ) &&
      !runtimeWorkspace.includes(
        "selected_clip_ids.push",
      ) &&
      !runtimeWorkspace.includes(
        "active_clip_id =",
      ),

    shell_has_no_direct_fetch:
      !timeline.includes(
        "fetch(",
      ) &&
      !shell.includes(
        "fetch(",
      ) &&
      !runtimeWorkspace.includes(
        "/selection/clip",
      ),

    shell_has_no_direct_mutation:
      !timeline.includes(
        "moveClip(",
      ) &&
      !timeline.includes(
        "deleteClip(",
      ) &&
      !timeline.includes(
        "timeline.revision++",
      ),
  };

  console.log(
    "=== Runtime-connected Timeline Selection UI ===",
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
    "\nDONE: Runtime-connected Timeline Selection UI test completed.",
  );
}

main();