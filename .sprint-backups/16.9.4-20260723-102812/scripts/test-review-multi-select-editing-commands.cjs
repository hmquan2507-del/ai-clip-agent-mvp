/* eslint-disable @typescript-eslint/no-require-imports */

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const read = (file) => fs.readFileSync(path.join(root, file), "utf8");

function main() {
  const apiContracts = read("src/features/review/api/timeline-contracts.ts");
  const apiClient = read("src/features/review/api/client.ts");
  const stateContracts = read("src/features/review/state/contracts.ts");
  const stateRuntime = read("src/features/review/state/runtime.ts");
  const reactContracts = read("src/features/review/react/contracts.ts");
  const provider = read("src/features/review/react/provider.tsx");
  const integrationContracts = read("src/features/review/integration/contracts.ts");
  const workspace = read("src/features/review/integration/runtime-workspace.tsx");
  const keyboard = read("src/features/review/integration/use-runtime-keyboard-editing.ts");
  const timeline = read("src/features/review/shell/timeline.tsx");

  const operations = ["move_clips", "duplicate_clips", "delete_clips"];
  const checks = {
    contracts_complete: operations.every((operation) => apiContracts.includes(`\"${operation}\"`)),
    api_paths_complete: ["/timeline/multi/move", "/timeline/multi/duplicate", "/timeline/multi/delete"].every((route) => apiClient.includes(route)),
    state_runtime_complete: ["moveClips(", "duplicateClips(", "deleteClips("].every((method) => stateRuntime.includes(method)),
    runtime_owns_expected_revision: stateRuntime.includes("expected_revision: revision"),
    provider_actions_complete: [stateContracts, reactContracts, provider].every((source) => ["moveClips", "duplicateClips", "deleteClips"].every((method) => source.includes(method))),
    command_intents_complete: operations.every((operation) => integrationContracts.includes(`operation: \"${operation}\"`)),
    workspace_delegates_once: ["actions.moveClips", "actions.duplicateClips", "actions.deleteClips"].every((call) => workspace.includes(call)),
    multi_selection_authoritative: timeline.includes("clipboard.selectedClipIds") && timeline.includes("hasMultiSelection"),
    multi_controls_rendered: timeline.includes("moveSelectedClips(-1)") && timeline.includes("moveSelectedClips(1)") && timeline.includes('operation: "duplicate_clips"') && timeline.includes('operation: "delete_clips"'),
    keyboard_uses_multi_commands: keyboard.includes('operation: "duplicate_clips"') && keyboard.includes('operation: "delete_clips"'),
    locked_selection_read_only: timeline.includes("clipboard.canCut") && timeline.includes("canEditMultiSelection"),
    no_direct_api_calls: !timeline.includes("fetch(") && !keyboard.includes("fetch("),
    no_direct_timeline_mutation: !timeline.includes(".splice(") && !timeline.includes(".push("),
  };

  console.log("=== Multi-select Editing Commands ===");
  for (const [name, value] of Object.entries(checks)) {
    console.log(`${name}: ${value}`);
    assert.equal(value, true, `${name} failed`);
  }
  console.log("\nDONE: Multi-select editing commands test completed.");
}

main();
