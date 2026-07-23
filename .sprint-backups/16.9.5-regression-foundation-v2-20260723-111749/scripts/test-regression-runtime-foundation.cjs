const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const ts = require("typescript");

require.extensions[".ts"] = function compile(module, filename) {
  const source = fs.readFileSync(filename, "utf8");
  const output = ts.transpileModule(source, {
    fileName: filename,
    compilerOptions: {
      target: ts.ScriptTarget.ES2022,
      module: ts.ModuleKind.CommonJS,
      moduleResolution: ts.ModuleResolutionKind.NodeJs,
      esModuleInterop: true,
    },
  });
  module._compile(output.outputText, filename);
};

function main() {
  const playbackRoot = path.resolve(__dirname, "../src/features/playback");
  const runtime = require(path.join(playbackRoot, "runtime", "index.ts"));
  const contracts = require(path.join(playbackRoot, "contracts", "index.ts"));
  const adapters = require(path.join(playbackRoot, "adapters", "index.ts"));

  assert.equal(typeof runtime.createPlaybackSessionRuntime, "function");
  assert.equal(typeof runtime.createPlayheadRuntime, "function");
  assert.equal(contracts.PLAYBACK_SESSION_CONTRACT_VERSION, "16.8.7.1");
  assert.equal(typeof adapters.HtmlVideoPreviewAdapter, "function");

  const broadBarrelReference = "../src/features/playback/" + "index.ts";
  const scripts = fs
    .readdirSync(__dirname)
    .filter(
      (name) =>
        name.endsWith(".cjs") &&
        name !== "test-regression-runtime-foundation.cjs" &&
        name !== "test-professional-playback-runtime.cjs",
    );

  for (const name of scripts) {
    const source = fs.readFileSync(path.join(__dirname, name), "utf8");
    assert.equal(
      source.includes(broadBarrelReference),
      false,
      `${name} still imports the broad playback barrel`,
    );
  }

  console.log("SPRINT 16.9.5 REGRESSION RUNTIME FOUNDATION: PASS");
}

main();
