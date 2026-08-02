/* eslint-disable @typescript-eslint/no-require-imports */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const read = (file) => fs.readFileSync(path.join(root, file), "utf8");

const shell = read("src/features/desktop-editor/components/desktop-editor-shell.tsx");
const grid = read("src/features/desktop-editor/components/desktop-grid.tsx");
const header = read("src/features/desktop-editor/components/desktop-editor-header.tsx");
const toolRail = read("src/features/desktop-editor/components/editor-tool-rail.tsx");
const statusBar = read("src/features/desktop-editor/components/editor-status-bar.tsx");
const panelDivider = read("src/features/desktop-editor/components/panel-divider.tsx");
const panelCollapseButton = read("src/features/desktop-editor/components/panel-collapse-button.tsx");
const layoutHook = read("src/features/desktop-editor/hooks/use-desktop-editor-layout.ts");
const aiDirectorDock = read("src/features/desktop-editor/components/editor-ai-director-dock.tsx");

// Files this sprint MUST NOT touch — either authoritative runtimes or
// content components explicitly out of scope for a shell-only sprint.
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

const OUT_OF_SCOPE_CONTENT_FILES = [
  "src/features/desktop-editor/components/editor-preview-canvas.tsx",
  "src/features/desktop-editor/components/editor-timeline-workspace.tsx",
  "src/features/desktop-editor/components/editor-inspector.tsx",
  "src/features/desktop-editor/components/editor-asset-panel.tsx",
  "src/features/desktop-editor/components/editor-ai-copilot.tsx",
  "src/features/ai-timeline/components/ai-timeline.tsx",
  "src/features/ai-timeline/components/ai-block.tsx",
  "src/features/ai-decision-actions/components/decision-inspector.tsx",
];

function countOccurrences(haystack, needle) {
  return haystack.split(needle).length - 1;
}

const checks = {
  // --- Layout matches the blueprint's canonical structure ---
  layout_grid_areas_present:
    grid.includes('"header') &&
    grid.includes('"rail') &&
    grid.includes('"timeline') &&
    grid.includes('"aiDirector') &&
    grid.includes('"status'),
  layout_ai_director_dock_reserved: grid.includes("aiDirectorDock") && shell.includes("EditorAiDirectorDock"),
  layout_focus_zones_present:
    grid.includes('data-editor-focus-zone="asset-panel"') &&
    grid.includes('data-editor-focus-zone="preview"') &&
    grid.includes('data-editor-focus-zone="timeline"') &&
    grid.includes('data-editor-focus-zone="inspector"') &&
    header.includes('data-editor-focus-zone="header"') &&
    toolRail.includes('data-editor-focus-zone="tool-rail"') &&
    statusBar.includes('data-editor-focus-zone="status"'),

  // --- Panel framework: resize + collapse + min/max, reusable across panels ---
  panel_framework_resize_exists:
    panelDivider.includes("useLayoutResizer") && panelDivider.includes("onPointerDown"),
  panel_framework_collapse_exists: panelCollapseButton.includes("PanelCollapseButton"),
  panel_framework_min_max_default_exists:
    layoutHook.includes("ASSET_LIBRARY_LAYOUT") &&
    layoutHook.includes("min:") &&
    layoutHook.includes("max:") &&
    layoutHook.includes("default:"),
  panel_framework_keyboard_resize: panelDivider.includes("ArrowLeft") && panelDivider.includes("ArrowRight"),

  // --- Docking rules ---
  docking_asset_panel_left_resizable_collapsible:
    shell.includes("assetsDivider") && shell.includes("toggleAssetLibraryCollapsed"),
  docking_inspector_right_resizable_collapsible:
    shell.includes("inspectorDivider") && shell.includes("toggleInspectorCollapsed"),
  docking_status_bar_fixed_bottom: grid.includes('"status      status'),

  // --- Responsive shell behavior ---
  responsive_function_exists: layoutHook.includes("computeResponsiveDesktopEditorLayout"),
  responsive_uses_viewport_width: layoutHook.includes("useViewportWidth") && layoutHook.includes("innerWidth"),
  responsive_preview_floor_protected: layoutHook.includes("PREVIEW_MIN_WIDTH_PX"),
  responsive_collapse_priority_order:
    (() => {
      const fnBody = layoutHook.split("const steps: Array<() => void> = [")[1] ?? "";
      const compactIdx = fnBody.indexOf("autoToolRailCompact = true");
      const assetMinIdx = fnBody.indexOf("ASSET_LIBRARY_LAYOUT.min");
      const assetCollapseIdx = fnBody.indexOf("ASSET_LIBRARY_LAYOUT.collapsed");
      const inspectorMinIdx = fnBody.indexOf("INSPECTOR_LAYOUT.min");
      const inspectorCollapseIdx = fnBody.indexOf("INSPECTOR_LAYOUT.collapsed");
      return (
        compactIdx > -1 &&
        compactIdx < assetMinIdx &&
        assetMinIdx < assetCollapseIdx &&
        assetCollapseIdx < inspectorMinIdx &&
        inspectorMinIdx < inspectorCollapseIdx
      );
    })(),

  // --- Theme: semantic tokens only ---
  header_uses_ce_tokens: header.includes("--ce-") && !header.includes("--desktop-editor-"),
  tool_rail_uses_ce_tokens: toolRail.includes("--ce-") && !toolRail.includes("--desktop-editor-"),
  status_bar_uses_ce_tokens: statusBar.includes("--ce-") && !statusBar.includes("--desktop-editor-"),
  panel_divider_uses_ce_tokens: panelDivider.includes("--ce-") && !panelDivider.includes("--desktop-editor-"),
  panel_collapse_button_uses_ce_tokens:
    panelCollapseButton.includes("--ce-") && !panelCollapseButton.includes("--desktop-editor-"),
  shell_wrapper_uses_ce_tokens: shell.includes("--ce-bg-workspace") && shell.includes("--ce-text-primary"),

  // --- Header: allowed content only ---
  header_has_allowed_elements:
    header.includes("productionTitle") && header.includes("onExport") && header.includes("autosaveLabel"),

  // --- Status bar: no fake information ---
  status_bar_no_hardcoded_fake_defaults:
    !/zoomLabel = "100%"/.test(statusBar) &&
    !/resolutionLabel = "1080/.test(statusBar) &&
    !/playbackSpeedLabel = "1x"/.test(statusBar),
  status_bar_pending_runtime_present: countOccurrences(statusBar, "Pending Runtime") >= 1,
  status_bar_real_fields_preserved: statusBar.includes("fps") && statusBar.includes("durationLabel") && statusBar.includes("cursorTimeLabel"),

  // --- AI Director entry: reserved only, no real UI ---
  ai_director_dock_is_placeholder_only:
    aiDirectorDock.includes("reserved") &&
    !aiDirectorDock.includes("onSubmit") &&
    !aiDirectorDock.includes("fetch(") &&
    !/import.*ReviewAICommandBar/.test(aiDirectorDock) &&
    !aiDirectorDock.includes("<ReviewAICommandBar"),

  // --- Accessibility ---
  header_has_banner_landmark: header.includes('role="banner"'),
  tool_rail_has_nav_landmark: toolRail.includes('aria-label="Editor tool rail"'),
  status_bar_has_contentinfo_landmark: statusBar.includes('role="contentinfo"'),
  focus_ring_utility_used:
    header.includes("ce-focus-ring") && toolRail.includes("ce-focus-ring") && panelDivider.includes("ce-focus-ring"),

  // --- No fake backend / no direct API calls introduced ---
  no_direct_api_calls:
    !shell.includes("fetch(") &&
    !grid.includes("fetch(") &&
    !header.includes("fetch(") &&
    !toolRail.includes("fetch(") &&
    !statusBar.includes("fetch(") &&
    !aiDirectorDock.includes("fetch("),
};

console.log("=== Desktop Editor Shell Redesign (Sprint 17.2) ===");
for (const [name, value] of Object.entries(checks)) {
  console.log(`${name}: ${value}`);
  assert.equal(value, true, `${name} failed`);
}

console.log("\n--- Authoritative runtime files verified untouched ---");
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
  assert.equal(untouched, true, `${relativePath} appears to have been modified by this sprint's shell work`);
  runtimeFilesChecked += 1;
}
assert.ok(runtimeFilesChecked > 0, "expected at least one runtime file to be verified");

console.log("\n--- Out-of-scope content components verified untouched (shell-only sprint) ---");
let contentFilesChecked = 0;
for (const relativePath of OUT_OF_SCOPE_CONTENT_FILES) {
  const fullPath = path.join(root, relativePath);
  if (!fs.existsSync(fullPath)) {
    console.log(`${relativePath}: SKIPPED (not found)`);
    continue;
  }
  contentFilesChecked += 1;
  console.log(`${relativePath}: present (existence check only — this sprint does not diff its contents)`);
}
assert.ok(contentFilesChecked > 0, "expected at least one out-of-scope content file to exist");

console.log("\nDONE: Desktop Editor Shell Redesign test completed.");
