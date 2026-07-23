const fs = require("node:fs");
const path = require("node:path");

const root = process.cwd();
const playback = path.join(root, "src", "features", "playback");

const required = new Map([
  ["contracts/professional-playback-contracts.ts", [
    "PROFESSIONAL_PLAYBACK_CONTRACT_VERSION",
    "ProfessionalPlaybackConfiguration",
    "ProfessionalPlaybackSnapshot",
    "ProfessionalPlaybackPorts",
  ]],
  ["runtime/playback-engine-runtime.ts", [
    "PlaybackSessionRuntime",
    "ProfessionalPlaybackConfiguration",
    "setInPoint",
    "setOutPoint",
    "setLoopMode",
    "stepForward",
    "stepBackward",
    "advance(nowMs",
    "j()",
    "k()",
    "l()",
  ]],
  ["runtime/timeline-professional-playback-runtime.ts", [
    "VideoPreviewSynchronizer",
    "AudioSynchronizationRuntime",
    "PlayheadRuntime",
    "handleKeyboardKey",
    "replaceBufferedRanges",
    "dispose",
  ]],
]);

for (const [relative, capabilities] of required) {
  const file = path.join(playback, relative);
  if (!fs.existsSync(file)) throw new Error(`Missing Sprint 16.9.5 v3 file: ${relative}`);
  const source = fs.readFileSync(file, "utf8");
  for (const capability of capabilities) {
    if (!source.includes(capability)) {
      throw new Error(`Missing Sprint 16.9.5 v3 capability: ${relative} -> ${capability}`);
    }
  }
}

const contracts = fs.readFileSync(
  path.join(playback, "contracts", "professional-playback-contracts.ts"),
  "utf8",
);
if (/export\s+type\s+PlaybackDirection\b/.test(contracts)) {
  throw new Error("Sprint 16.9.5 v3 must reuse the existing PlaybackDirection contract.");
}
if (!contracts.includes("import type") || !contracts.includes("PlaybackDirection")) {
  throw new Error("Sprint 16.9.5 v3 must import PlaybackDirection from the existing contract.");
}

const contractIndex = fs.readFileSync(path.join(playback, "contracts", "index.ts"), "utf8");
const exportCount = (contractIndex.match(/professional-playback-contracts/g) || []).length;
if (exportCount !== 1) {
  throw new Error(`Expected one professional playback contract export, found ${exportCount}.`);
}

const runtimeIndex = fs.readFileSync(path.join(playback, "runtime", "index.ts"), "utf8");
for (const name of [
  "playback-engine-runtime",
  "timeline-professional-playback-runtime",
]) {
  const count = (runtimeIndex.match(new RegExp(name, "g")) || []).length;
  if (count !== 1) throw new Error(`Expected one ${name} export, found ${count}.`);
}

console.log("SPRINT 16.9.5 V3 PROFESSIONAL PLAYBACK RUNTIME: PASS");
