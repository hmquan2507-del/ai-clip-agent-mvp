/* eslint-disable @typescript-eslint/no-require-imports */

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");

function read(relativePath) {
  return fs.readFileSync(
    path.join(root, relativePath),
    "utf8",
  );
}

function main() {
  const contracts = read(
    "src/features/review/integration/contracts.ts",
  );
  const adapter = read(
    "src/features/review/integration/adapters.ts",
  );
  const workspace = read(
    "src/features/review/integration/runtime-workspace.tsx",
  );
  const shell = read(
    "src/features/review/shell/review-editor-shell.tsx",
  );
  const panels = read(
    "src/features/review/shell/workspace-panels.tsx",
  );

  const operations = [
    "refresh_suggestions",
    "select_suggestion",
    "apply_suggestion",
    "dismiss_suggestion",
    "regenerate_suggestions",
  ];

  const runtimeMethods = [
    "refreshAISuggestions",
    "selectAISuggestion",
    "applyAISuggestion",
    "dismissAISuggestion",
    "regenerateAISuggestions",
  ];

  const shellSources = [shell, panels].join("\n");

  const checks = {
    suggestion_intents_complete:
      operations.every((operation) =>
        contracts.includes(`\"${operation}\"`),
      ),
    authoritative_snapshot_mapped:
      adapter.includes("state.suggestionSnapshot") &&
      adapter.includes("suggestionSnapshot?.read_model") &&
      adapter.includes("selected_suggestion_id"),
    lifecycle_metadata_mapped:
      adapter.includes("lifecycle_revision") &&
      adapter.includes("timeline_revision") &&
      adapter.includes("actionable_count") &&
      adapter.includes("stale_count"),
    runtime_actions_delegated:
      runtimeMethods.every((method) =>
        workspace.includes(`actions.${method}(`),
      ),
    provider_boundary_preserved:
      workspace.includes("useReviewWorkspaceActions") &&
      workspace.includes("onAISuggestionCommand"),
    shell_forwards_suggestion_intents:
      shell.includes("onSuggestionIntent") &&
      shell.includes("onAISuggestionCommand"),
    suggestion_list_rendered:
      panels.includes("suggestions.map") &&
      panels.includes("suggestion.title") &&
      panels.includes("suggestion.description"),
    review_controls_complete:
      panels.includes("Áp dụng") &&
      panels.includes("Bỏ qua") &&
      panels.includes("Tạo lại đề xuất"),
    stale_suggestion_read_only:
      panels.includes("suggestion.stale") &&
      panels.includes("!suggestion.actionable"),
    pending_state_visible:
      adapter.includes('state.pendingOperation === "ai_suggestion"') &&
      panels.includes("Đang xử lý…") &&
      panels.includes("animate-spin"),
    controls_disabled_atomically:
      shell.includes("clipboardPending ||") &&
      shell.includes("suggestionPending") &&
      panels.includes("disabled={pending}"),
    apply_uses_authoritative_id:
      panels.includes("suggestionId: suggestion.id") &&
      workspace.includes("suggestion_id:") &&
      workspace.includes("intent.suggestionId"),
    no_optimistic_suggestion_state:
      !workspace.includes("useState(") &&
      !panels.includes("useState("),
    no_direct_api_calls:
      !shellSources.includes("fetch(") &&
      !shellSources.includes("/api/v1/") &&
      !workspace.includes("fetch("),
    no_direct_timeline_mutation:
      !shellSources.includes("timeline.clips.push") &&
      !shellSources.includes("timeline.tracks.push") &&
      !workspace.includes("timeline.clips.push"),
  };

  console.log("=== Runtime-connected AI Suggestion Review UI ===");

  for (const [name, value] of Object.entries(checks)) {
    console.log(`${name}: ${value}`);
    assert.equal(value, true, `${name} failed`);
  }

  console.log(
    "\nDONE: Runtime-connected AI suggestion review UI test completed.",
  );
}

main();
