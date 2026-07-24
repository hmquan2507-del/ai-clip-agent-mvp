/* eslint-disable @typescript-eslint/no-require-imports */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = process.cwd();
const read = (relativePath) => fs.readFileSync(path.join(root, relativePath), "utf8");
const exists = (relativePath) => fs.existsSync(path.join(root, relativePath));

const checks = {
  workspace_route_exists: exists("src/app/workspace/page.tsx"),
  editor_route_exists: exists("src/app/editor/[productionId]/page.tsx"),
  legacy_review_preserved: exists("src/app/review/page.tsx"),
  legacy_upload_preserved: exists("src/app/upload/page.tsx"),
  legacy_export_preserved: exists("src/app/export/page.tsx"),
  legacy_productions_preserved: exists("src/app/productions/page.tsx"),
  editor_reuses_review_runtime: read("src/app/editor/[productionId]/page.tsx").includes("DesktopEditorRuntimeAdapter"),
  editor_accepts_dynamic_id: read("src/app/editor/[productionId]/page.tsx").includes("productionId"),
  workspace_feature_connected: read("src/app/workspace/page.tsx").includes("WorkspaceHome"),
  navigation_promotes_workspace: read("src/components/navigation/sidebar.tsx").includes('href: "/workspace"'),
  production_cards_open_editor: read("src/features/production/production-card.tsx").includes("/editor/"),
};

for (const [name, value] of Object.entries(checks)) {
  console.log(`${name}: ${value}`);
  assert.equal(value, true, `${name} failed`);
}

console.log("SPRINT 16.10.2 WORKSPACE FOUNDATION: PASS");
