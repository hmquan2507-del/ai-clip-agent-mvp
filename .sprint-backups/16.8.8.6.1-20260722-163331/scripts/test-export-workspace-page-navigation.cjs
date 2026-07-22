const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");

function read(relativePath) {
  const fullPath = path.join(root, relativePath);
  assert.ok(fs.existsSync(fullPath), `Missing file: ${relativePath}`);
  return fs.readFileSync(fullPath, "utf8");
}

const navigation = read(
  "src/features/export-workspace/navigation/review-to-export.ts",
);
const page = read(
  "src/features/export-workspace/components/export-workspace-page.tsx",
);
const route = read("src/app/export/page.tsx");
const topbar = read(
  "src/features/review/shell/editor-topbar.tsx",
);
const shell = read(
  "src/features/review/shell/review-editor-shell.tsx",
);
const runtime = read(
  "src/features/review/integration/runtime-workspace.tsx",
);

assert.match(navigation, /REVIEW_EXPORT_STORAGE_KEY/);
assert.match(navigation, /sessionStorage/);
assert.match(navigation, /isExportRenderContract/);
assert.match(navigation, /extractExportRenderContract/);
assert.match(navigation, /production_id/);
assert.match(navigation, /source: "review"/);

assert.match(page, /readReviewToExportContract/);
assert.match(page, /ExportRuntimePanel/);
assert.match(page, /Back to review/);
assert.match(page, /No immutable render contract found/);

assert.match(route, /production_id/);
assert.match(route, /ExportWorkspacePage/);

assert.match(topbar, /onExport/);
assert.match(topbar, /exportDisabled/);
assert.doesNotMatch(topbar, /href="\/export"/);

assert.match(shell, /onExport/);
assert.match(shell, /exportDisabled/);
assert.match(runtime, /storeReviewToExportContract/);
assert.match(runtime, /buildExportWorkspaceHref/);
assert.match(runtime, /router\.push/);
assert.match(runtime, /exportDisabled\s*=\s*\{!renderContract\}/);

console.log(
  "SPRINT 16.8.6 EXPORT WORKSPACE PAGE INTEGRATION "
    + "& REVIEW-TO-EXPORT NAVIGATION: PASS",
);
console.log("export_page_integrated: True");
console.log("production_query_forwarded: True");
console.log("immutable_contract_handoff: True");
console.log("session_storage_envelope: True");
console.log("review_export_action_connected: True");
console.log("missing_contract_safe_state: True");
console.log("back_navigation_connected: True");
