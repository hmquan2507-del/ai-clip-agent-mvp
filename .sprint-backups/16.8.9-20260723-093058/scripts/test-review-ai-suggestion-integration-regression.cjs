/* eslint-disable @typescript-eslint/no-require-imports */

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { spawnSync } = require("node:child_process");

const frontendRoot = path.resolve(__dirname, "..");
const repositoryRoot = path.resolve(frontendRoot, "..");

const regressionScripts = [
  "test-review-ai-suggestion-api-state-runtime.cjs",
  "test-review-ai-suggestion-react-provider-hooks.cjs",
  "test-review-runtime-ai-suggestion-review-ui.cjs",
  "test-review-ai-command-submission-boundary.cjs",
  "test-review-runtime-timeline-selection-ui.cjs",
  "test-review-runtime-timeline-command-controls.cjs",
  "test-review-timeline-clipboard-ui-integration.cjs",
  "test-review-drag-drop-integration-regression.cjs",
];

function read(relativePath) {
  return fs.readFileSync(
    path.join(frontendRoot, relativePath),
    "utf8",
  );
}

function runRegressions() {
  for (const script of regressionScripts) {
    const result = spawnSync(
      process.execPath,
      [path.join(frontendRoot, "scripts", script)],
      {
        cwd: frontendRoot,
        encoding: "utf8",
      },
    );

    if (result.stdout) {
      process.stdout.write(result.stdout);
    }
    if (result.stderr) {
      process.stderr.write(result.stderr);
    }

    assert.equal(
      result.status,
      0,
      `${script} exited with status ${result.status}`,
    );
  }
}

function main() {
  runRegressions();

  const apiClient = read(
    "src/features/review/api/client.ts",
  );
  const stateRuntime = read(
    "src/features/review/state/runtime.ts",
  );
  const provider = read(
    "src/features/review/react/provider.tsx",
  );
  const workspace = read(
    "src/features/review/integration/runtime-workspace.tsx",
  );
  const adapter = read(
    "src/features/review/integration/adapters.ts",
  );
  const shell = [
    read("src/features/review/shell/review-editor-shell.tsx"),
    read("src/features/review/shell/workspace-panels.tsx"),
    read("src/features/review/shell/ai-command-bar.tsx"),
  ].join("\n");

  const methods = [
    "getAISuggestions",
    "selectAISuggestion",
    "applyAISuggestion",
    "dismissAISuggestion",
    "regenerateAISuggestions",
  ];

  const checks = {
    all_suggestion_regressions_passed: true,
    api_surface_complete:
      methods.every((method) => apiClient.includes(`${method}(`)),
    state_runtime_is_authoritative:
      stateRuntime.includes("suggestionSnapshot") &&
      stateRuntime.includes("validateAISuggestionResponse") &&
      stateRuntime.includes("recoverAISuggestionConflict"),
    provider_is_action_boundary:
      provider.includes("runtime.applyAISuggestion(") &&
      provider.includes("runtime.regenerateAISuggestions("),
    workspace_delegates_intents:
      workspace.includes("actions.applyAISuggestion(") &&
      workspace.includes("actions.dismissAISuggestion(") &&
      workspace.includes("actions.regenerateAISuggestions("),
    ui_uses_authoritative_read_model:
      adapter.includes("state.suggestionSnapshot") &&
      adapter.includes("suggestionSnapshot?.read_model"),
    stale_apply_blocked:
      shell.includes("suggestion.stale") &&
      shell.includes("!suggestion.actionable"),
    pending_controls_atomic:
      shell.includes("suggestionPending") &&
      shell.includes("disabled={pending}"),
    no_optimistic_suggestion_state:
      !workspace.includes("useState(") &&
      !read(
        "src/features/review/shell/workspace-panels.tsx",
      ).includes("useState("),
    no_direct_api_calls:
      !workspace.includes("fetch(") &&
      !shell.includes("fetch(") &&
      !shell.includes("/api/v1/"),
    no_direct_timeline_mutation:
      !shell.includes("timeline.clips.push") &&
      !shell.includes("timeline.tracks.push"),
    natural_language_boundary_preserved:
      stateRuntime.includes("submitAICommand(") &&
      workspace.includes("actions.submitAICommand(") &&
      shell.includes("onAICommandSubmit") &&
      !shell.includes("/commands/submit"),
    command_submission_never_mutates_timeline:
      stateRuntime.includes("timeline_mutated !== false") &&
      apiClient.includes("payload.timeline_mutated !== false"),
    backend_integration_present:
      fs.existsSync(
        path.join(
          repositoryRoot,
          "backend/scripts/test_review_ai_suggestion_api_integration.py",
        ),
      ),
  };

  console.log("=== AI Suggestion Integration & Regression ===");

  for (const [name, value] of Object.entries(checks)) {
    console.log(`${name}: ${value}`);
    assert.equal(value, true, `${name} failed`);
  }

  console.log(
    "\nDONE: AI suggestion integration and regression test completed.",
  );
}

main();
