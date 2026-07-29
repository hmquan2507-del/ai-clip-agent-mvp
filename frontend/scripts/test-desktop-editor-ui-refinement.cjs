/* eslint-disable @typescript-eslint/no-require-imports */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const read = (file) => fs.readFileSync(path.join(root, file), "utf8");

const layout = read("src/features/desktop-editor/hooks/use-desktop-editor-layout.ts");
const assetPanel = read("src/features/desktop-editor/components/editor-asset-panel.tsx");
const header = read("src/features/desktop-editor/components/desktop-editor-header.tsx");
const inspector = read("src/features/desktop-editor/components/editor-inspector.tsx");
const copilot = read("src/features/desktop-editor/components/editor-ai-copilot.tsx");
const shell = read("src/features/desktop-editor/components/desktop-editor-shell.tsx");
const aiBlock = read("src/features/ai-timeline/components/ai-block.tsx");
const aiTimeline = read("src/features/ai-timeline/components/ai-timeline.tsx");
const decisionInspector = read("src/features/ai-decision-actions/components/decision-inspector.tsx");
const globalsCss = read("src/app/globals.css");

const touchedFiles = {
  layout,
  assetPanel,
  header,
  inspector,
  copilot,
  shell,
  aiBlock,
  aiTimeline,
  decisionInspector,
};

const checks = {
  // Requirement 1 — Preview priority: Asset/Inspector defaults narrowed, Tool Rail shrunk.
  preview_priority_asset_default_narrowed:
    layout.includes("default: 300") && layout.includes("max: 320"),
  preview_priority_inspector_default_narrowed:
    layout.includes("default: 320") && layout.includes("max: 340"),
  preview_priority_tool_rail_narrowed: layout.includes("expanded: 64"),

  // Requirement 2 — compact Asset Panel.
  asset_panel_two_column_grid: assetPanel.includes("grid-cols-2"),
  asset_panel_duration_overlay: assetPanel.includes("absolute bottom-1 right-1"),
  asset_panel_more_menu: assetPanel.includes('aria-haspopup="menu"') && assetPanel.includes("OVERFLOW_COLLECTIONS"),
  asset_panel_still_resizable_collapsible:
    assetPanel.includes("onToggleCollapsed") && layout.includes("ASSET_LIBRARY_LAYOUT"),

  // Requirement 3 — Timeline Workspace sizing preserved (40-45% of editor height, still resizable).
  timeline_layout_present:
    layout.includes("TIMELINE_LAYOUT") && layout.includes("default: 320") && layout.includes("min: 240"),
  header_toolbar_grouped: header.includes('role="group"') && header.includes('aria-label="History"'),

  // Requirement 4 — AI decision block metadata / readability.
  ai_block_min_width_handling: aiBlock.includes("COMPACT_WIDTH_THRESHOLD") && aiBlock.includes("MIN_HIT_WIDTH"),
  ai_block_conditional_confidence: aiBlock.includes("CONFIDENCE_WIDTH_THRESHOLD") && aiBlock.includes("showConfidence"),
  ai_timeline_empty_state: aiTimeline.includes("emptyStateMessage"),
  ai_timeline_tooltip_clamping: read("src/features/ai-timeline/components/ai-tooltip.tsx").includes("overflowsRight"),

  // Requirement 5 — Inspector visual consolidation (tabs unchanged: Properties/AI Copilot/Decision).
  inspector_tabs_unchanged:
    inspector.includes('label="Properties"') &&
    inspector.includes('label="AI Copilot"') &&
    inspector.includes('label="Decision"'),
  inspector_uses_compact_scroll: inspector.includes("desktop-editor-scroll"),
  inspector_still_wires_decision_tab: inspector.includes("AiDecisionInspector") && inspector.includes("useAiDecisionActions"),

  // Requirement 6 — AI Copilot: Quick Actions / Suggestions / AI Director, sticky, pending-runtime messaging.
  copilot_has_quick_actions_suggestions: copilot.includes("Quick actions") && copilot.includes("Suggestions"),
  copilot_ai_director_present: copilot.includes("AI Director"),
  copilot_ai_director_sticky: copilot.includes("sticky bottom-0"),
  copilot_pending_runtime_badge: copilot.includes("Pending runtime"),
  copilot_reuses_review_command_bar: copilot.includes("ReviewAICommandBar"),

  // Requirement 7 — design tokens (reused/extended, not a new palette).
  ai_timeline_theme_has_parity_tokens:
    globalsCss.includes("--ai-timeline-danger-text") &&
    globalsCss.includes("--ai-timeline-success-text") &&
    globalsCss.includes("--ai-timeline-focus"),
  desktop_editor_theme_has_named_categories:
    globalsCss.includes("--desktop-editor-hover") &&
    globalsCss.includes("--desktop-editor-selection") &&
    globalsCss.includes("--desktop-editor-focus") &&
    globalsCss.includes("--desktop-editor-disabled-text") &&
    globalsCss.includes("--desktop-editor-error") &&
    globalsCss.includes("--desktop-editor-processing"),
  compact_scrollbar_utility_present: globalsCss.includes(".desktop-editor-scroll"),

  // Requirement 8 — responsive collapse behavior still available for every resizable panel.
  responsive_collapse_state_present:
    layout.includes("assetLibraryCollapsed") &&
    layout.includes("inspectorCollapsed") &&
    layout.includes("timelineCollapsed") &&
    layout.includes("toolRailCompact"),

  // AI Decision Action Runtime (16.10.6) integration must remain intact — literal
  // strings the existing test-ai-decision-action-runtime.cjs also relies on.
  decision_action_provider_untouched: shell.includes("<AiDecisionActionProvider>"),
  decision_timeline_wiring_intact:
    aiTimeline.includes("decisionActions.selectDecision(block)") && aiTimeline.includes("decisionActions.runAction"),
  decision_pending_runtime_copy_intact: decisionInspector.includes("No timeline mutation was faked"),

  // No direct API calls or Timeline Runtime mutation calls introduced by this
  // visual-only pass, across every file this sprint touched.
  no_direct_api_calls: Object.values(touchedFiles).every((source) => !source.includes("fetch(")),
  no_timeline_runtime_mutation: Object.values(touchedFiles).every(
    (source) =>
      !source.includes("ReviewTimelineRuntime") &&
      !/\b(moveClip|trimClipStart|trimClipEnd|splitClip|deleteClip)\s*\(/.test(source),
  ),
};

console.log("=== Desktop Editor UI/UX Refinement (16.10.6.1) ===");

for (const [name, value] of Object.entries(checks)) {
  console.log(`${name}: ${value}`);
  assert.equal(value, true, `${name} failed`);
}

console.log("\nDONE: Desktop Editor UI/UX refinement test completed.");
