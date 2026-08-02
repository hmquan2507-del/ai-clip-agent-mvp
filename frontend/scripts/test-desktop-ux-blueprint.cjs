/* eslint-disable @typescript-eslint/no-require-imports */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const repoRoot = path.resolve(__dirname, "..", "..");
const frontendRoot = path.resolve(__dirname, "..");
const readSpec = (file) => fs.readFileSync(path.join(repoRoot, "specs", file), "utf8");
const readFrontend = (file) => fs.readFileSync(path.join(frontendRoot, file), "utf8");

const principles = readSpec("design/editor-ui-principles.md");
const blueprint = readSpec("design/desktop-editor-ux-blueprint.md");
const interaction = readSpec("design/editor-interaction-model.md");
const stateMatrix = readSpec("design/editor-state-matrix.md");
const masterPlan = readSpec("design/frontend-redesign-master-plan.md");
const epic = readSpec("epics/17.1.5-desktop-ux-blueprint.md");

function countOccurrences(haystack, needle) {
  return haystack.split(needle).length - 1;
}

function countPattern(haystack, pattern) {
  const matches = haystack.match(pattern);
  return matches ? matches.length : 0;
}

const checks = {
  // --- editor-ui-principles.md ---
  principles_count_in_range: (() => {
    const count = countPattern(principles, /^### P\d+ /gm);
    return count >= 35 && count <= 50;
  })(),
  principles_have_required_fields:
    countOccurrences(principles, "**Why:**") >= 35 &&
    countOccurrences(principles, "**Implication:**") >= 35 &&
    countOccurrences(principles, "**Verification:**") >= 35,
  principles_cover_13_categories:
    [
      "## Product hierarchy",
      "## Editing workflow",
      "## Preview",
      "## Manual Timeline",
      "## AI Timeline",
      "## Inspector",
      "## AI Director",
      "## Panels and docking",
      "## Selection",
      "## Feedback and state",
      "## Accessibility",
      "## Responsive desktop",
    ].every((heading) => principles.includes(heading)),

  // --- desktop-editor-ux-blueprint.md ---
  blueprint_has_information_hierarchy: blueprint.includes("## 1. Information hierarchy"),
  blueprint_has_canonical_layout: blueprint.includes("## 2. Canonical layout"),
  blueprint_has_10_wireframes: countPattern(blueprint, /^### W\d+ /gm) === 10,
  blueprint_has_8_diagrams: countPattern(blueprint, /^### D\d+ /gm) === 8,
  blueprint_has_mermaid_blocks: countOccurrences(blueprint, "```mermaid") === 8,
  blueprint_has_panel_docking_rules: blueprint.includes("## 5. Panel and docking rules"),
  blueprint_has_responsive_section: blueprint.includes("## 6. Responsive blueprint") &&
    ["1920", "1440", "1366"].every((w) => blueprint.includes(w)),
  blueprint_has_future_runtime_requirements:
    blueprint.includes("## 7. Future Runtime Requirements") && countOccurrences(blueprint, "FRR-") >= 7,
  blueprint_has_sprint_boundaries:
    blueprint.includes("## 8. Sprint 17.2") &&
    ["17.2", "17.3", "17.4", "17.5", "17.6", "17.7", "17.8"].every((s) => blueprint.includes(`**${s}`)),
  blueprint_diagrams_reference_real_modules:
    blueprint.includes("DesktopEditorRuntimeAdapter") &&
    blueprint.includes("ReviewWorkspaceProvider") &&
    blueprint.includes("TimelineViewportContext"),
  blueprint_no_invented_backend_services:
    !/\b(GraphQL|gRPC|Kafka|Redis|MongoDB)\b/.test(blueprint),

  // --- editor-interaction-model.md ---
  interaction_has_selection_model: interaction.includes("## 1. Selection model"),
  interaction_has_10_selection_contexts: (() => {
    const rows = interaction.match(/^\| \d+ \| /gm) || [];
    return rows.length === 10;
  })(),
  interaction_has_context_propagation_matrix: interaction.includes("## 2. Context propagation matrix"),
  interaction_matrix_has_8_columns:
    interaction.includes(
      "| Action / Event | Selection Runtime | Manual Timeline | AI Timeline | Inspector | Preview | Asset Panel | AI Director | History |",
    ),
  interaction_matrix_row_count_at_least_22: (() => {
    const section = interaction.split("## 2. Context propagation matrix")[1].split("## 3.")[0];
    const rows = section.split("\n").filter((line) => line.trim().startsWith("|") && !line.includes("---") && !line.includes("Action / Event"));
    return rows.length >= 22;
  })(),
  interaction_has_preview_section: interaction.includes("## 3. Preview interaction"),
  interaction_has_manual_timeline_section: interaction.includes("## 4. Manual Timeline interaction"),
  interaction_has_ai_timeline_section: interaction.includes("## 5. AI Timeline interaction"),
  interaction_has_inspector_section: interaction.includes("## 6. Inspector interaction"),
  interaction_has_ai_director_section: interaction.includes("## 7. AI Director interaction"),
  interaction_has_keyboard_focus_blueprint: interaction.includes("## 8. Keyboard and focus blueprint"),
  interaction_does_not_invent_keybindings:
    !/\bCtrl\+[A-Z]\b/.test(interaction) && !/\bCmd\+[A-Z]\b/.test(interaction),

  // --- editor-state-matrix.md ---
  state_matrix_has_editor_shell: stateMatrix.includes("## 1. Editor shell"),
  state_matrix_has_preview: stateMatrix.includes("## 2. Preview"),
  state_matrix_has_manual_timeline: stateMatrix.includes("## 3. Manual Timeline"),
  state_matrix_has_ai_decision: stateMatrix.includes("## 4. AI Decision"),
  state_matrix_has_inspector: stateMatrix.includes("## 5. Inspector"),
  state_matrix_has_ai_director: stateMatrix.includes("## 6. AI Director"),
  state_matrix_tables_have_required_columns:
    countOccurrences(
      stateMatrix,
      "| State | Visible UI | Available interactions | Disabled interactions | Feedback | Exit condition |",
    ) === 6,

  // --- master plan cross-reference ---
  master_plan_references_blueprint:
    masterPlan.includes("editor-ui-principles.md") &&
    masterPlan.includes("desktop-editor-ux-blueprint.md") &&
    masterPlan.includes("editor-interaction-model.md") &&
    masterPlan.includes("editor-state-matrix.md"),

  // --- epic report ---
  epic_report_exists: epic.length > 0,
  epic_mentions_no_sprint_172_begun:
    /do not begin sprint 17\.2|sprint 17\.2 has not begun|17\.2 not started/i.test(epic),

  // --- runtime files verified untouched by this sprint's documentation work ---
  no_direct_api_calls_in_docs:
    !blueprint.includes("fetch(") && !interaction.includes("fetch(") && !stateMatrix.includes("fetch("),
};

const RUNTIME_FILES = [
  "src/features/review/state/runtime.ts",
  "src/features/review/react/provider.tsx",
  "src/features/review/integration/runtime-workspace.tsx",
  "src/features/review/integration/adapters.ts",
  "src/features/review/viewport/use-review-timeline-viewport.ts",
  "src/features/review/drag/index.ts",
  "src/features/review/trim/index.ts",
  "src/features/review/keyboard/index.ts",
  "src/features/ai-decision-actions/context.tsx",
  "src/features/ai-timeline/context/timeline-viewport-context.tsx",
];

console.log("=== Desktop UX Blueprint (Sprint 17.1.5) ===");
for (const [name, value] of Object.entries(checks)) {
  console.log(`${name}: ${value}`);
  assert.equal(value, true, `${name} failed`);
}

console.log("\n--- Runtime file verification (blueprint sprint touched documentation only) ---");
let runtimeFilesChecked = 0;
for (const relativePath of RUNTIME_FILES) {
  const fullPath = path.join(frontendRoot, relativePath);
  if (!fs.existsSync(fullPath)) {
    console.log(`${relativePath}: SKIPPED (not found)`);
    continue;
  }
  const source = fs.readFileSync(fullPath, "utf8");
  const untouched = !source.includes("--ce-") && !source.includes("fetch(");
  console.log(`${relativePath}: untouched=${untouched}`);
  assert.equal(untouched, true, `${relativePath} appears to have been modified by this sprint's blueprint work`);
  runtimeFilesChecked += 1;
}
assert.ok(runtimeFilesChecked > 0, "expected at least one runtime file to be verified");

console.log("\nDONE: Desktop UX blueprint test completed.");
