const path = require("node:path");

const playbackRoot = path.resolve(__dirname, "../src/features/playback");

module.exports = {
  ...require(path.join(playbackRoot, "contracts", "index.ts")),
  ...require(path.join(playbackRoot, "runtime", "index.ts")),
  ...require(path.join(playbackRoot, "adapters", "index.ts")),
};
