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
  const helperPath = path.resolve(
    __dirname,
    "./playback-headless-test-api.cjs",
  );
  const api = require(helperPath);

  assert.equal(typeof api.createPlaybackSessionRuntime, "function");
  assert.equal(typeof api.createPlayheadRuntime, "function");
  assert.equal(typeof api.createAudioSynchronizationRuntime, "function");
  assert.equal(typeof api.createVideoPreviewSynchronizer, "function");

  const broadBarrelReference =
    "../src/features/playback/" + "index.ts";

  const violations = fs
    .readdirSync(__dirname)
    .filter((name) => name.endsWith(".cjs"))
    .filter((name) => {
      if (name === "test-regression-runtime-foundation.cjs") {
        return false;
      }
      const source = fs.readFileSync(path.join(__dirname, name), "utf8");
      return source.includes(broadBarrelReference);
    });

  assert.deepEqual(
    violations,
    [],
    `Regression scripts still importing broad playback barrel: ${violations.join(", ")}`,
  );

  console.log("SPRINT 16.9.5 REGRESSION RUNTIME FOUNDATION V2: PASS");
}

main();
