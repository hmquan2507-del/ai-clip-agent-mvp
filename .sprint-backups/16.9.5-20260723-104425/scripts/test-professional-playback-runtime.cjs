const fs = require("fs");
const path = require("path");
const ts = require("typescript");

const root = path.resolve(__dirname, "..");
const required = [
  "playback/contracts/professional-playback-contracts.ts",
  "playback/runtime/playback-clock-runtime.ts",
  "playback/runtime/playback-speed-runtime.ts",
  "playback/runtime/playback-loop-runtime.ts",
  "playback/runtime/playback-cache-runtime.ts",
  "playback/runtime/playback-buffer-runtime.ts",
  "playback/runtime/playback-sync-runtime.ts",
  "playback/runtime/playback-engine-runtime.ts",
  "playback/runtime/timeline-professional-playback-runtime.ts",
];

for (const relative of required) {
  const file = path.join(root, relative);
  if (!fs.existsSync(file)) throw new Error(`Missing ${relative}`);
  const content = fs.readFileSync(file, "utf8");
  const result = ts.transpileModule(content, {
    compilerOptions: {
      target: ts.ScriptTarget.ES2020,
      module: ts.ModuleKind.CommonJS,
      strict: true,
      esModuleInterop: true,
    },
    reportDiagnostics: true,
    fileName: file,
  });
  const errors = (result.diagnostics || []).filter((d) => d.category === ts.DiagnosticCategory.Error);
  if (errors.length) {
    throw new Error(errors.map((d) => ts.flattenDiagnosticMessageText(d.messageText, "\n")).join("\n"));
  }
}

const engineSource = fs.readFileSync(path.join(root, "playback/runtime/playback-engine-runtime.ts"), "utf8");
for (const token of ["stepForward", "stepBackward", "enableInOutLoop", "advance(nowMs", "j()", "k()", "l()"]) {
  if (!engineSource.includes(token)) throw new Error(`Missing engine capability: ${token}`);
}
const timelineSource = fs.readFileSync(path.join(root, "playback/runtime/timeline-professional-playback-runtime.ts"), "utf8");
for (const token of ["handleKeyboardKey", "synchronizeMedia", "updateBufferedRanges", "dispose"]) {
  if (!timelineSource.includes(token)) throw new Error(`Missing timeline capability: ${token}`);
}
console.log("SPRINT 16.9.5 PROFESSIONAL PLAYBACK RUNTIME: PASS");
