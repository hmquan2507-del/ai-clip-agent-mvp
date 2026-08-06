/* eslint-disable @typescript-eslint/no-require-imports */
//
// Real end-to-end API integration test: boots the actual FastAPI backend
// as a child process against a throwaway SQLite DB, then drives the exact
// HTTP contract the frontend uses - upload a real video, open a Review
// Workspace session, make a real timeline edit, submit a render, and
// download the resulting file - asserting on real HTTP responses and real
// bytes on disk. No source-file string matching.
//
// Previous versions of this script (before the upload -> edit -> render
// pipeline repair) only ran `fs.readFileSync` over source files and
// asserted `string.includes(...)` - that never proved the API worked,
// only that certain identifiers existed in the source text.
const assert = require("node:assert/strict");
const { spawn } = require("node:child_process");
const fs = require("node:fs");
const path = require("node:path");

const backendRoot = path.resolve(__dirname, "..", "..", "backend");
const pythonBin = path.join(
  backendRoot,
  ".venv",
  "Scripts",
  "python.exe",
);
const testDbPath = path.join(
  backendRoot,
  "data",
  "test_e2e_api_integration.db",
);
const sampleVideoPath = path.join(
  backendRoot,
  "storage",
  "render_artifact_test",
  "221e4b01-5fb9-4b4a-a549-4fb32c455059",
  "artifacts",
  "final.mp4",
);

const PORT = 8731;
const BASE_URL = `http://127.0.0.1:${PORT}`;
const API_URL = `${BASE_URL}/api/v1`;

function run(command, args, options = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      cwd: backendRoot,
      ...options,
    });
    let stdout = "";
    let stderr = "";
    child.stdout?.on("data", (chunk) => (stdout += chunk));
    child.stderr?.on("data", (chunk) => (stderr += chunk));
    child.on("close", (code) => {
      if (code === 0) {
        resolve({ stdout, stderr });
      } else {
        reject(
          new Error(
            `${command} ${args.join(" ")} exited ${code}\n${stderr}`,
          ),
        );
      }
    });
  });
}

async function waitForHealth(timeoutMs = 30000) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    try {
      const response = await fetch(`${BASE_URL}/health`);
      if (response.ok) return;
    } catch {
      // server not up yet
    }
    await new Promise((resolve) => setTimeout(resolve, 300));
  }
  throw new Error("Backend did not become healthy in time.");
}

async function main() {
  fs.rmSync(testDbPath, { force: true });

  console.log("=== Real End-to-End API Integration Test ===");

  const seed = await run(pythonBin, [
    "scripts/seed_e2e_test_production.py",
    "--db-path",
    testDbPath,
  ]);
  const productionId = seed.stdout.trim();
  assert.ok(
    /^[0-9a-f-]{36}$/i.test(productionId),
    `seed script did not print a production id: ${seed.stdout}`,
  );
  console.log("seeded_production_id:", productionId);

  const server = spawn(
    pythonBin,
    [
      "-m",
      "uvicorn",
      "app.main:app",
      "--port",
      String(PORT),
    ],
    {
      cwd: backendRoot,
      env: {
        ...process.env,
        DATABASE_URL: `sqlite:///${testDbPath}`,
      },
    },
  );

  let serverLog = "";
  server.stdout?.on("data", (chunk) => (serverLog += chunk));
  server.stderr?.on("data", (chunk) => (serverLog += chunk));

  const checks = {};

  try {
    await waitForHealth();
    checks.backend_boots_and_is_healthy = true;

    // --- Real upload ---
    const videoBytes = fs.readFileSync(sampleVideoPath);
    const form = new FormData();
    form.append(
      "file",
      new Blob([videoBytes], { type: "video/mp4" }),
      "source.mp4",
    );

    const uploadResponse = await fetch(
      `${API_URL}/uploads/production/${productionId}/source-video`,
      { method: "POST", body: form },
    );
    const uploadBody = await uploadResponse.json();
    checks.upload_succeeds = uploadResponse.status === 201;
    checks.upload_has_real_duration =
      typeof uploadBody.duration === "number" &&
      uploadBody.duration > 0;

    // --- Real Review Workspace session + real timeline edit ---
    const sessionResponse = await fetch(
      `${API_URL}/productions/${productionId}/review/session`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          force_refresh: true,
          replace_existing: true,
        }),
      },
    );
    const sessionBody = await sessionResponse.json();
    checks.review_session_opens = sessionResponse.status === 200;

    const sessionId = sessionBody.session_id;
    const tracks = sessionBody.snapshot?.timeline?.tracks ?? [];
    const primaryTrack = tracks.find(
      (track) => track.track_type === "video_primary",
    );
    const primaryClip = primaryTrack?.clips?.[0];
    checks.session_has_a_real_primary_clip = Boolean(primaryClip);

    let trimmedEndTime = null;
    if (primaryClip) {
      trimmedEndTime = Math.max(
        1,
        Number(primaryClip.end_time) - 2,
      );

      const trimResponse = await fetch(
        `${API_URL}/productions/${productionId}/review/timeline/trim-end`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            session_id: sessionId,
            clip_id: primaryClip.clip_id,
            new_end_time: trimmedEndTime,
          }),
        },
      );
      const trimBody = await trimResponse.json();
      checks.timeline_trim_succeeds = trimResponse.status === 200;
      checks.trim_reflected_in_response =
        trimBody?.snapshot?.timeline?.tracks
          ?.flatMap((t) => t.clips)
          ?.some((c) => c.end_time === trimmedEndTime) ?? false;
    }

    // --- Real render, through the exact endpoint the frontend calls ---
    const renderResponse = await fetch(
      `${API_URL}/render/${productionId}`,
      { method: "POST" },
    );
    const renderBody = await renderResponse.json();
    console.log("render_response:", renderBody);
    checks.render_endpoint_returns_202 = renderResponse.status === 202;
    checks.render_actually_completes =
      renderBody.status === "completed";

    // --- Real download of the real rendered artifact ---
    const downloadResponse = await fetch(
      `${API_URL}/productions/${productionId}/download`,
    );
    checks.download_returns_real_video =
      downloadResponse.status === 200 &&
      downloadResponse.headers.get("content-type") === "video/mp4";

    const downloaded = Buffer.from(
      await downloadResponse.arrayBuffer(),
    );
    checks.downloaded_file_is_nonempty = downloaded.length > 1000;
    // MP4 files carry an "ftyp" box near the start of the file.
    checks.downloaded_file_is_a_real_mp4 = downloaded
      .subarray(0, 64)
      .includes("ftyp");
  } finally {
    server.kill();
    await new Promise((resolve) => setTimeout(resolve, 500));
    try {
      fs.rmSync(testDbPath, { force: true });
    } catch {
      // Windows can briefly hold the sqlite file handle after the
      // uvicorn process exits - harmless, the next run overwrites it.
    }
  }

  for (const [name, value] of Object.entries(checks)) {
    console.log(`${name}: ${value}`);
  }

  const failed = Object.entries(checks).filter(([, v]) => v !== true);
  if (failed.length > 0) {
    console.log("\n--- server log tail ---");
    console.log(serverLog.slice(-4000));
  }

  for (const [name, value] of Object.entries(checks)) {
    assert.equal(value, true, `${name} failed`);
  }

  console.log(
    "\nDONE: Real end-to-end API integration test completed successfully.",
  );
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
