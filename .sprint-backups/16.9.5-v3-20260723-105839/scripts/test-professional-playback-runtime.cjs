const fs = require("node:fs");
const path = require("node:path");

const root = process.cwd();
const playback = path.join(root, "src", "features", "playback");

const checks = [
  ["contracts/professional-playback-contracts.ts", [
    "PlaybackConfiguration",
    "PlaybackSnapshot",
    "PlaybackMetrics",
    "PlaybackHistoryPort",
    "PlaybackMediaPort",
    "PlaybackSchedulerPort",
  ]],
  ["runtime/playback-clock-runtime.ts", [
    "export class PlaybackClockRuntime",
    "tick(",
    "reset(",
  ]],
  ["runtime/playback-speed-runtime.ts", [
    "export class PlaybackSpeedRuntime",
    "shuttleForward",
    "shuttleReverse",
    "setDirection",
  ]],
  ["runtime/playback-loop-runtime.ts", [
    "export class PlaybackLoopRuntime",
    "setMode",
    "resolve(",
    "getLoopCount",
  ]],
  ["runtime/playback-cache-runtime.ts", [
    "export class PlaybackCacheRuntime",
    "prefetchKeys",
    "stats()",
  ]],
  ["runtime/playback-buffer-runtime.ts", [
    "export class PlaybackBufferRuntime",
    "secondsAhead",
    "snapshot(",
  ]],
  ["runtime/playback-sync-runtime.ts", [
    "export class PlaybackSyncRuntime",
    "synchronize(",
    "setViewport",
  ]],
  ["runtime/playback-engine-runtime.ts", [
    "export class PlaybackEngineRuntime",
    "togglePlayPause",
    "stepForward",
    "stepBackward",
    "enableInOutLoop",
    "advance(nowMs",
    "j()",
    "k()",
    "l()",
    "snapshot()",
    "restore(",
  ]],
  ["runtime/timeline-professional-playback-runtime.ts", [
    "export class TimelineProfessionalPlaybackRuntime",
    "handleKeyboardKey",
    "synchronizeMedia",
    "updateBufferedRanges",
    "dispose",
  ]],
];

for (const [relative, symbols] of checks) {
  const file = path.join(playback, relative);
  if (!fs.existsSync(file)) throw new Error(`Missing 16.9.5 file: ${relative}`);
  const source = fs.readFileSync(file, "utf8");
  for (const symbol of symbols) {
    if (!source.includes(symbol)) {
      throw new Error(`Missing 16.9.5 capability: ${relative} -> ${symbol}`);
    }
  }
  if (relative.startsWith("runtime/") && /\b(document|window|HTMLElement|React)\b/.test(source)) {
    throw new Error(`Professional playback runtime must remain DOM/React independent: ${relative}`);
  }
}

for (const [relative, symbol] of [
  ["contracts/index.ts", 'export * from "./professional-playback-contracts"'],
  ["runtime/index.ts", 'export * from "./timeline-professional-playback-runtime"'],
  ["runtime/index.ts", 'export * from "./playback-engine-runtime"'],
]) {
  const source = fs.readFileSync(path.join(playback, relative), "utf8");
  if (!source.includes(symbol)) throw new Error(`Missing 16.9.5 export: ${relative} -> ${symbol}`);
}

console.log("SPRINT 16.9.5 PROFESSIONAL PLAYBACK RUNTIME: PASS");
