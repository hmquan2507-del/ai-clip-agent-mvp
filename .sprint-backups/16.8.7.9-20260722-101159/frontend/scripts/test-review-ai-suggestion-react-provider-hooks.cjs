/* eslint-disable @typescript-eslint/no-require-imports */

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const React = require("react");
const { renderToStaticMarkup } = require("react-dom/server");
const ts = require("typescript");

function compileTypeScript(module, filename) {
  const source = fs.readFileSync(filename, "utf8");
  const output = ts.transpileModule(source, {
    fileName: filename,
    compilerOptions: {
      target: ts.ScriptTarget.ES2022,
      module: ts.ModuleKind.CommonJS,
      moduleResolution: ts.ModuleResolutionKind.NodeJs,
      jsx: ts.JsxEmit.ReactJSX,
      esModuleInterop: true,
    },
  });
  module._compile(output.outputText, filename);
}

require.extensions[".ts"] = compileTypeScript;
require.extensions[".tsx"] = compileTypeScript;

const root = path.resolve(__dirname, "..");
const providerSource = fs.readFileSync(
  path.join(root, "src/features/review/react/provider.tsx"),
  "utf8",
);
const hooksSource = fs.readFileSync(
  path.join(root, "src/features/review/react/hooks.ts"),
  "utf8",
);

const {
  createReviewWorkspaceSessionRuntime,
} = require(path.join(
  root,
  "src/features/review/state/index.ts",
));

const {
  ReviewWorkspaceProvider,
  useReviewAISuggestionActions,
  useReviewAISuggestions,
  useReviewWorkspaceStatus,
} = require(path.join(
  root,
  "src/features/review/react/index.ts",
));

const productionId =
  "221e4b01-5fb9-4b4a-a549-4fb32c455059";
const calls = [];

const client = new Proxy({}, {
  get(_target, name) {
    return async () => {
      calls.push(String(name));
      throw new Error("Not expected during server render.");
    };
  },
});

function main() {
  const runtime = createReviewWorkspaceSessionRuntime({ client });
  const captured = {};

  function Probe() {
    const actions = useReviewAISuggestionActions();
    const suggestions = useReviewAISuggestions();
    const status = useReviewWorkspaceStatus();

    captured.actions = [
      actions.refreshAISuggestions,
      actions.selectAISuggestion,
      actions.applyAISuggestion,
      actions.dismissAISuggestion,
      actions.regenerateAISuggestions,
    ];
    captured.suggestions = suggestions;
    captured.status = status;

    return React.createElement("div", null, "ai-suggestion-provider-ready");
  }

  const html = renderToStaticMarkup(
    React.createElement(
      ReviewWorkspaceProvider,
      {
        productionId,
        runtime,
        autoOpen: false,
        autoLoadSuggestions: false,
      },
      React.createElement(Probe),
    ),
  );

  const delegatedMethods = [
    "refreshAISuggestions",
    "selectAISuggestion",
    "applyAISuggestion",
    "dismissAISuggestion",
    "regenerateAISuggestions",
  ];

  const checks = {
    provider_rendered:
      html.includes("ai-suggestion-provider-ready"),
    suggestion_hook_available:
      captured.actions.every((action) => typeof action === "function"),
    suggestion_actions_complete:
      delegatedMethods.every((method) =>
        providerSource.includes(`runtime.${method}(`),
      ),
    provider_delegates_to_runtime:
      providerSource.includes("refreshAISuggestions") &&
      providerSource.includes("autoLoadSuggestions"),
    initial_suggestion_state_valid:
      captured.suggestions.snapshot === null &&
      captured.suggestions.available === false &&
      captured.suggestions.pending === false &&
      captured.suggestions.suggestions.length === 0 &&
      captured.suggestions.selectedSuggestion === null,
    suggestion_status_available:
      captured.status.pendingSuggestionOperation === null &&
      captured.status.suggesting === false,
    runtime_state_authoritative:
      hooksSource.includes("suggestionSnapshot?.read_model.suggestions") &&
      hooksSource.includes("selected_suggestion_id"),
    no_local_suggestion_state:
      !hooksSource.includes("useState(") &&
      !hooksSource.includes("useReducer("),
    no_direct_api_calls:
      !providerSource.includes("fetch(") &&
      !hooksSource.includes("fetch("),
    no_direct_timeline_mutation:
      !providerSource.includes("timeline.clips") &&
      !hooksSource.includes("timeline.clips"),
    server_render_read_only:
      calls.length === 0,
  };

  console.log("=== React AI Suggestion Provider & Hooks ===");

  for (const [name, value] of Object.entries(checks)) {
    console.log(`${name}: ${value}`);
    assert.equal(value, true, `${name} failed`);
  }

  runtime.dispose();
  console.log("\nDONE: React AI suggestion provider and hooks test completed.");
}

main();
