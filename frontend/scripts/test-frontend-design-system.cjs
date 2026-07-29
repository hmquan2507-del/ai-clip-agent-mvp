/* eslint-disable @typescript-eslint/no-require-imports */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const read = (file) => fs.readFileSync(path.join(root, file), "utf8");

const css = read("src/app/globals.css");

// Runtime files that MUST NOT have been touched by this sprint's token work —
// tokens live only in CSS/component files, never in runtime logic.
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

function countOccurrences(haystack, needle) {
  return haystack.split(needle).length - 1;
}

const checks = {
  // Semantic color tokens exist (Task 4).
  background_tokens_exist:
    css.includes("--ce-bg-app:") &&
    css.includes("--ce-bg-workspace:") &&
    css.includes("--ce-bg-panel:") &&
    css.includes("--ce-bg-panel-raised:") &&
    css.includes("--ce-bg-canvas:") &&
    css.includes("--ce-bg-overlay:"),
  border_tokens_exist:
    css.includes("--ce-border-subtle:") &&
    css.includes("--ce-border-default:") &&
    css.includes("--ce-border-strong:") &&
    css.includes("--ce-border-focus:"),
  text_tokens_exist:
    css.includes("--ce-text-primary:") &&
    css.includes("--ce-text-secondary:") &&
    css.includes("--ce-text-muted:") &&
    css.includes("--ce-text-disabled:") &&
    css.includes("--ce-text-inverse:"),
  accent_tokens_exist:
    css.includes("--ce-accent-primary:") &&
    css.includes("--ce-accent-primary-hover:") &&
    css.includes("--ce-accent-primary-active:") &&
    css.includes("--ce-accent-soft:"),

  // State tokens.
  state_tokens_exist:
    css.includes("--ce-state-selected:") &&
    css.includes("--ce-state-hover:") &&
    css.includes("--ce-state-focus:") &&
    css.includes("--ce-state-processing:") &&
    css.includes("--ce-state-success:") &&
    css.includes("--ce-state-warning:") &&
    css.includes("--ce-state-error:") &&
    css.includes("--ce-state-disabled:"),

  // Timeline tokens.
  timeline_tokens_exist:
    css.includes("--ce-timeline-video:") &&
    css.includes("--ce-timeline-audio:") &&
    css.includes("--ce-timeline-subtitle:") &&
    css.includes("--ce-timeline-broll:") &&
    css.includes("--ce-timeline-ai:") &&
    css.includes("--ce-timeline-playhead:") &&
    css.includes("--ce-timeline-selection:"),

  // AI decision lifecycle tokens.
  decision_lifecycle_tokens_exist:
    css.includes("--ce-decision-draft:") &&
    css.includes("--ce-decision-applied:") &&
    css.includes("--ce-decision-accepted:") &&
    css.includes("--ce-decision-rejected:") &&
    css.includes("--ce-decision-disabled:") &&
    css.includes("--ce-decision-manual:") &&
    css.includes("--ce-decision-processing:") &&
    css.includes("--ce-decision-stale:") &&
    css.includes("--ce-decision-error:"),

  // Typography roles exist (as CSS variables + utility classes).
  typography_roles_exist:
    [
      "display",
      "page-title",
      "panel-title",
      "section-title",
      "body",
      "body-compact",
      "label",
      "metadata",
      "caption",
      "timeline-label",
      "button",
      "input",
      "code",
    ].every((role) => css.includes(`.ce-text-${role} {`)),

  // Spacing scale exists.
  spacing_scale_exists:
    css.includes("--ce-space-2xs:") &&
    css.includes("--ce-space-xs:") &&
    css.includes("--ce-space-sm:") &&
    css.includes("--ce-space-md:") &&
    css.includes("--ce-space-lg:") &&
    css.includes("--ce-space-xl:") &&
    css.includes("--ce-space-2xl:"),

  // Editor dimensions exist.
  editor_dimensions_exist:
    css.includes("--ce-dim-header-height:") &&
    css.includes("--ce-dim-tool-rail-width:") &&
    css.includes("--ce-dim-asset-panel-min:") &&
    css.includes("--ce-dim-asset-panel-default:") &&
    css.includes("--ce-dim-asset-panel-max:") &&
    css.includes("--ce-dim-inspector-min:") &&
    css.includes("--ce-dim-inspector-default:") &&
    css.includes("--ce-dim-inspector-max:") &&
    css.includes("--ce-dim-timeline-toolbar-height:") &&
    css.includes("--ce-dim-track-height:") &&
    css.includes("--ce-dim-ai-timeline-height-default:") &&
    css.includes("--ce-dim-control-height-sm:") &&
    css.includes("--ce-icon-size-sm:"),

  // Radius / elevation / motion scales exist.
  radius_scale_exists:
    css.includes("--ce-radius-sm:") &&
    css.includes("--ce-radius-md:") &&
    css.includes("--ce-radius-lg:") &&
    css.includes("--ce-radius-pill:"),
  elevation_scale_exists:
    css.includes("--ce-shadow-panel:") &&
    css.includes("--ce-shadow-floating:") &&
    css.includes("--ce-shadow-accent:"),
  motion_tokens_exist:
    css.includes("--ce-motion-duration-fast:") &&
    css.includes("--ce-motion-duration-base:") &&
    css.includes("--ce-motion-duration-slow:") &&
    css.includes("--ce-motion-easing-standard:"),

  // Focus styles exist.
  focus_styles_exist: css.includes(".ce-focus-ring:focus-visible") && css.includes("--ce-border-focus"),

  // Reduced-motion handling exists app-wide (not just scoped to one legacy theme).
  reduced_motion_app_wide:
    countOccurrences(css, "prefers-reduced-motion: reduce") >= 2 &&
    /\*,\s*\*::before,\s*\*::after\s*\{/.test(css) &&
    css.includes("scroll-behavior: auto !important;"),

  // No duplicate theme root was introduced — still exactly the 3 legacy
  // `*-theme {` scopes, and the new tokens live in a plain `:root` block,
  // not a 4th competing theme class.
  no_duplicate_theme_root:
    (css.match(/-theme\s*\{/g) || []).length === 3 && countOccurrences(css, "--ce-bg-app: #0b0d12;") === 1,

  // No direct API calls introduced anywhere in this sprint's CSS.
  no_direct_api_calls: !css.includes("fetch("),
};

console.log("=== Frontend Design System Foundation (Sprint 17.1) ===");
for (const [name, value] of Object.entries(checks)) {
  console.log(`${name}: ${value}`);
  assert.equal(value, true, `${name} failed`);
}

// Existing runtime files were not modified — tokens must not leak into
// runtime logic files (they belong only in CSS/component files).
console.log("\n--- Runtime file verification (no --ce- tokens leaked into runtime logic) ---");
let runtimeFilesChecked = 0;
for (const relativePath of RUNTIME_FILES) {
  const fullPath = path.join(root, relativePath);
  if (!fs.existsSync(fullPath)) {
    console.log(`${relativePath}: SKIPPED (not found)`);
    continue;
  }
  const source = fs.readFileSync(fullPath, "utf8");
  const untouched = !source.includes("--ce-") && !source.includes("fetch(");
  console.log(`${relativePath}: untouched=${untouched}`);
  assert.equal(untouched, true, `${relativePath} appears to have been modified by this sprint's token work`);
  runtimeFilesChecked += 1;
}
assert.ok(runtimeFilesChecked > 0, "expected at least one runtime file to be verified");

console.log("\nDONE: Frontend design system foundation test completed.");
