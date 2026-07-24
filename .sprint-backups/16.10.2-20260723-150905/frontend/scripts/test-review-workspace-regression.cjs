/* eslint-disable @typescript-eslint/no-require-imports */

const assert = require(
  "node:assert/strict",
);

const fs = require("node:fs");
const path = require("node:path");

const {
  spawnSync,
} = require("node:child_process");

const frontendRoot =
  path.resolve(__dirname, "..");

const repositoryRoot =
  path.resolve(frontendRoot, "..");

const regressionScripts = [
  "test-review-api-client.cjs",
  "test-review-workspace-session-runtime.cjs",
  "test-review-workspace-react-runtime.cjs",
  "test-review-design-system.cjs",
  "test-review-editor-shell.cjs",
  "test-review-runtime-connected-ui.cjs",
  "test-review-timeline-trim-coordinate-model.cjs",
  "test-review-timeline-trim-session-runtime.cjs",
  "test-review-runtime-clip-trim-handles.cjs",
  "test-review-timeline-keyboard-shortcut-runtime.cjs",
  "test-review-runtime-keyboard-editing-controls.cjs",
  "test-review-timeline-zoom-scroll-runtime.cjs",
  "test-review-runtime-timeline-zoom-scroll-ui.cjs",
  "test-review-multi-select-editing-commands.cjs",
  "test-review-ai-command-submission-boundary.cjs",
  "test-review-ai-suggestion-integration-regression.cjs",
  "test-review-drag-drop-integration-regression.cjs",
];

const removedLegacyFiles = [
  "src/features/review/ai-suggestions.tsx",
  "src/features/review/review-actions.tsx",
  "src/features/review/review-sidebar.tsx",
  "src/features/review/subtitle-preview.tsx",
  "src/features/review/transcript-panel.tsx",
  "src/features/review/video-preview-panel.tsx",
  "src/features/review/page.tsx",
];

function read(relativePath) {
  return fs.readFileSync(
    path.join(
      frontendRoot,
      relativePath,
    ),
    "utf8",
  );
}

function runRegressionScripts() {
  for (
    const script
    of regressionScripts
  ) {
    const result = spawnSync(
      process.execPath,
      [
        path.join(
          frontendRoot,
          "scripts",
          script,
        ),
      ],
      {
        cwd: frontendRoot,
        encoding: "utf8",
      },
    );

    if (result.stdout) {
      process.stdout.write(
        result.stdout,
      );
    }

    if (result.stderr) {
      process.stderr.write(
        result.stderr,
      );
    }

    assert.equal(
      result.status,
      0,
      `${script} exited with status ${result.status}`,
    );
  }
}

function main() {
  runRegressionScripts();

  const shellFiles = [
    "src/features/review/shell/review-editor-shell.tsx",
    "src/features/review/shell/editor-topbar.tsx",
    "src/features/review/shell/editor-rail.tsx",
    "src/features/review/shell/workspace-panels.tsx",
    "src/features/review/shell/timeline.tsx",
    "src/features/review/shell/ai-command-bar.tsx",
  ];

  const shellSource =
    shellFiles
      .map(read)
      .join("\n");

  const runtimeSource = read(
    "src/features/review/integration/runtime-workspace.tsx",
  );

  const adapterSource = read(
    "src/features/review/integration/adapters.ts",
  );

  const routeSource = read(
    "src/app/review/page.tsx",
  );

  const reviewIndex = read(
    "src/features/review/index.ts",
  );

  const backendMain =
    fs.readFileSync(
      path.join(
        repositoryRoot,
        "backend/app/main.py",
      ),
      "utf8",
    );

  const backendConfig =
    fs.readFileSync(
      path.join(
        repositoryRoot,
        "backend/app/core/config.py",
      ),
      "utf8",
    );

  const forbiddenMutationCallPatterns = [
    "move_clip",
    "trim_clip_start",
    "trim_clip_end",
    "insert_clip",
    "delete_clip",
    "split_clip",
    "duplicate_clip",
    "close_gap",
  ].map(
    (mutation) =>
      new RegExp(
        `\\b${mutation}\\s*\\(`,
      ),
  );

  const checks = {
    all_regression_scripts_passed:
      true,

    legacy_ui_removed:
      removedLegacyFiles.every(
        (file) =>
          !fs.existsSync(
            path.join(
              frontendRoot,
              file,
            ),
          ),
      ),

    shell_has_no_direct_fetch:
      !shellSource.includes(
        "fetch(",
      ),

    shell_has_no_api_paths:
      !shellSource.includes(
        "/api/",
      ),

    shell_has_no_direct_mutations:
      forbiddenMutationCallPatterns.every(
        (pattern) =>
          !pattern.test(shellSource),
      ),

    provider_is_runtime_boundary:
      runtimeSource.includes(
        "ReviewWorkspaceProvider",
      ) &&
      runtimeSource.includes(
        "useReviewWorkspaceState",
      ) &&
      runtimeSource.includes(
        "useReviewWorkspaceActions",
      ),

    snapshot_adapter_is_used:
      runtimeSource.includes(
        "buildReviewEditorViewModel",
      ) &&
      adapterSource.includes(
        "ReviewRuntimeSessionSnapshot",
      ),

    route_accepts_production_id:
      routeSource.includes(
        "production_id",
      ) &&
      routeSource.includes(
        "productionId={productionId}",
      ),

    old_exports_removed:
      !reviewIndex.includes(
        "AISuggestions",
      ) &&
      !reviewIndex.includes(
        "ReviewSidebar",
      ) &&
      !reviewIndex.includes(
        "VideoPreviewPanel",
      ),

    cors_middleware_registered:
      backendMain.includes(
        "CORSMiddleware",
      ) &&
      backendMain.includes(
        "allow_origins=settings.cors_origins",
      ),

    cors_origins_configurable:
      backendConfig.includes(
        "cors_allowed_origins",
      ) &&
      backendConfig.includes(
        "def cors_origins",
      ),

    ai_command_uses_submission_boundary:
      shellSource.includes(
        "onAICommandSubmit",
      ) &&
      runtimeSource.includes(
        "actions.submitAICommand",
      ) &&
      !shellSource.includes(
        "/commands/submit",
      ),
  };

  console.log(
    "=== Review Workspace Integration & Regression ===",
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
    "\nDONE: Review Workspace "
      + "integration and regression "
      + "test completed.",
  );
}

main();
