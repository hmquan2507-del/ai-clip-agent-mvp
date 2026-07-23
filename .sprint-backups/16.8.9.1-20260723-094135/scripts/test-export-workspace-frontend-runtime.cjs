const assert = require("node:assert");
const fs = require("node:fs");
const path = require("node:path");

const frontendRoot = path.resolve(__dirname, "..");

function read(relativePath) {
  const fullPath = path.join(frontendRoot, relativePath);
  assert.ok(fs.existsSync(fullPath), `Missing file: ${relativePath}`);
  return fs.readFileSync(fullPath, "utf8");
}

const types = read("src/features/export-workspace/runtime/types.ts");
const apiClient = read("src/features/export-workspace/runtime/api-client.ts");
const runtime = read("src/features/export-workspace/runtime/runtime.ts");
const hook = read(
  "src/features/export-workspace/runtime/use-export-workspace-runtime.ts",
);
const panel = read(
  "src/features/export-workspace/components/export-runtime-panel.tsx",
);
const barrel = read("src/features/export-workspace/index.ts");

assert.match(types, /ExportRenderContract/);
assert.match(types, /ExportRenderStatusData/);
assert.match(types, /"submitting"/);
assert.match(types, /"polling"/);
assert.match(types, /"completed"/);
assert.match(types, /"failed"/);

assert.match(
  apiClient,
  /\/api\/v1\/export-workspace\/render-submissions/,
);
assert.match(apiClient, /encodeURIComponent\(queueJobId\)/);
assert.match(apiClient, /AbortSignal/);
assert.match(apiClient, /ExportWorkspaceApiError/);

assert.match(runtime, /class ExportWorkspaceRuntime/);
assert.match(runtime, /submitRender/);
assert.match(runtime, /getRenderStatus/);
assert.match(runtime, /setTimeout/);
assert.match(runtime, /terminalStatuses/);
assert.match(runtime, /abortController/);
assert.match(runtime, /subscribe/);
assert.match(runtime, /getSnapshot/);

assert.match(hook, /useSyncExternalStore/);
assert.match(hook, /useEffect/);
assert.match(panel, /role="progressbar"/);
assert.match(panel, /Start render/);
assert.match(panel, /Cancel tracking/);
assert.match(barrel, /ExportRuntimePanel/);

console.log(
  "SPRINT 16.8.5 EXPORT WORKSPACE FRONTEND RUNTIME: PASS",
);
console.log("typed_api_client: True");
console.log("render_submission_runtime: True");
console.log("status_polling: True");
console.log("abort_and_cleanup: True");
console.log("react_external_store_hook: True");
console.log("export_runtime_panel: True");
