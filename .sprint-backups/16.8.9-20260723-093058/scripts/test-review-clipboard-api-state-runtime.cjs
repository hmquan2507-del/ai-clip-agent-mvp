/* eslint-disable @typescript-eslint/no-require-imports */

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const ts = require("typescript");


const ROOT = process.cwd();
const REVIEW_ROOT = path.join(
  ROOT,
  "src/features/review",
);


function compileReviewModules(outputRoot) {
  for (const folder of ["api", "state"]) {
    const sourceFolder = path.join(
      REVIEW_ROOT,
      folder,
    );
    const outputFolder = path.join(
      outputRoot,
      folder,
    );
    fs.mkdirSync(outputFolder, {
      recursive: true,
    });

    for (const filename of fs.readdirSync(sourceFolder)) {
      if (!filename.endsWith(".ts")) {
        continue;
      }
      const source = fs.readFileSync(
        path.join(sourceFolder, filename),
        "utf8",
      );
      const compiled = ts.transpileModule(source, {
        compilerOptions: {
          target: ts.ScriptTarget.ES2022,
          module: ts.ModuleKind.CommonJS,
          esModuleInterop: true,
        },
        fileName: filename,
      });
      fs.writeFileSync(
        path.join(
          outputFolder,
          filename.replace(/\.ts$/, ".js"),
        ),
        compiled.outputText,
        "utf8",
      );
    }
  }
}


function makeSnapshot(
  productionId,
  sessionId,
  revision,
  itemCount = 0,
) {
  return {
    session: {
      session_id: sessionId,
      production_id: productionId,
      status: "ready",
      active: true,
      ready: true,
      closed: false,
      timeline_revision: revision,
      dirty: revision > 1,
      revision,
      created_at: "2026-07-18T00:00:00Z",
      updated_at: "2026-07-18T00:00:00Z",
      closed_at: null,
      error: null,
      metadata: {},
    },
    timeline: {
      production_id: productionId,
      revision,
      tracks: [],
      clip_count: revision,
    },
    clipboard: {
      state: {
        production_id: productionId,
        status: itemCount ? "ready" : "empty",
        available: itemCount > 0,
        item_count: itemCount,
        clip_count: itemCount,
        clipboard_id: "clipboard-1",
        last_action: itemCount ? "copy" : null,
        source_track_ids: itemCount ? ["video"] : [],
      },
      content: {
        clipboard_id: "clipboard-1",
        production_id: productionId,
        action: "copy",
        status: itemCount ? "ready" : "empty",
        available: itemCount > 0,
        item_count: itemCount,
        clip_count: itemCount,
        source_track_ids: itemCount ? ["video"] : [],
        anchor_time: 0,
        total_duration: itemCount,
        created_at: "2026-07-18T00:00:00Z",
        items: [],
        metadata: {},
      },
    },
    history: {
      production_id: productionId,
      can_undo: revision > 1,
      can_redo: false,
      undo_count: Math.max(0, revision - 1),
      redo_count: 0,
      current_revision: revision,
      maximum_history_size: 100,
      next_undo_label: null,
      next_redo_label: null,
    },
    metadata: {},
  };
}


function makeClipboardResponse(
  productionId,
  sessionId,
  operation,
  previousRevision,
  itemCount = 1,
) {
  const timelineChanging =
    operation === "cut" || operation === "paste";
  const currentRevision =
    previousRevision + (timelineChanging ? 1 : 0);
  return {
    contract_version: "16.4.8",
    success: true,
    operation,
    production_id: productionId,
    session_id: sessionId,
    previous_revision: previousRevision,
    current_revision: currentRevision,
    snapshot: makeSnapshot(
      productionId,
      sessionId,
      currentRevision,
      operation === "clear_content" ? 0 : itemCount,
    ),
    clipboard: {
      state: {},
      content: {},
      event: null,
      history_state: {},
      history: [],
    },
    timeline_history: timelineChanging
      ? { success: true }
      : null,
    metadata: {},
  };
}


function deferred() {
  let resolve;
  let reject;
  const promise = new Promise((yes, no) => {
    resolve = yes;
    reject = no;
  });
  return { promise, resolve, reject };
}


async function main() {
  const outputRoot = fs.mkdtempSync(
    path.join(ROOT, ".review-clipboard-test-"),
  );

  try {
    compileReviewModules(outputRoot);

    const api = require(
      path.join(outputRoot, "api/index.js"),
    );
    const stateModule = require(
      path.join(outputRoot, "state/runtime.js"),
    );

    const productionId =
      "221e4b01-5fb9-4b4a-a549-4fb32c455059";
    const sessionId = "clipboard-frontend-session";

    const requests = [];
    const fetcher = async (url, init) => {
      const body = JSON.parse(init.body);
      requests.push({
        url: String(url),
        method: init.method,
        body,
        signal: init.signal,
        headers: new Headers(init.headers),
      });
      const operationByPath = {
        "/clipboard/copy": "copy",
        "/clipboard/cut": "cut",
        "/clipboard/paste": "paste",
        "/clipboard/history/restore": "restore_history",
        "/clipboard": "clear_content",
        "/clipboard/history": "clear_history",
      };
      const pathname = new URL(url).pathname;
      const suffix = Object.keys(operationByPath)
        .sort((a, b) => b.length - a.length)
        .find((item) => pathname.endsWith(item));
      const operation = operationByPath[suffix];
      return new Response(
        JSON.stringify(
          makeClipboardResponse(
            productionId,
            body.session_id,
            operation,
            body.expected_revision,
          ),
        ),
        {
          status: 200,
          headers: {
            "Content-Type": "application/json",
          },
        },
      );
    };

    const client = api.createReviewWorkspaceClient({
      baseUrl: "http://localhost:8000/api/v1/",
      fetch: fetcher,
    });
    const controller = new AbortController();

    await client.copyTimelineClips(
      productionId,
      {
        session_id: sessionId,
        clip_ids: [" clip_1 ", "clip_1", "clip_2"],
        expected_revision: 4,
      },
      { signal: controller.signal },
    );
    await client.cutTimelineClips(
      productionId,
      {
        session_id: sessionId,
        clip_ids: ["clip_1"],
        expected_revision: 4,
      },
    );
    await client.pasteTimelineClips(
      productionId,
      {
        session_id: sessionId,
        at_time: 8.5,
        target_track_id: " video_overlay ",
        track_mapping: {
          " video ": " video_overlay ",
        },
        expected_revision: 5,
      },
    );
    await client.restoreTimelineClipboardHistory(
      productionId,
      {
        session_id: sessionId,
        entry_id: "history_1",
        expected_revision: 6,
      },
    );
    await client.clearTimelineClipboard(
      productionId,
      {
        session_id: sessionId,
        expected_revision: 6,
      },
    );
    await client.clearTimelineClipboardHistory(
      productionId,
      {
        session_id: sessionId,
        expected_revision: 6,
      },
    );

    let invalidClipIdsBlocked = false;
    try {
      await client.copyTimelineClips(productionId, {
        session_id: sessionId,
        clip_ids: ["", "   "],
        expected_revision: 6,
      });
    } catch {
      invalidClipIdsBlocked = true;
    }

    let invalidTimeBlocked = false;
    try {
      await client.pasteTimelineClips(productionId, {
        session_id: sessionId,
        at_time: -1,
        expected_revision: 6,
      });
    } catch {
      invalidTimeBlocked = true;
    }

    const runtimeCalls = [];
    let activeSnapshot = makeSnapshot(
      productionId,
      sessionId,
      1,
      0,
    );
    const runtimeClient = {
      async openSession() {
        return {
          production_id: productionId,
          session_id: sessionId,
          session: activeSnapshot.session,
          snapshot: activeSnapshot,
        };
      },
      async getSnapshot() {
        return {
          production_id: productionId,
          session_id: sessionId,
          snapshot: activeSnapshot,
        };
      },
    };

    for (const [method, operation] of [
      ["copyTimelineClips", "copy"],
      ["cutTimelineClips", "cut"],
      ["pasteTimelineClips", "paste"],
      ["restoreTimelineClipboardHistory", "restore_history"],
      ["clearTimelineClipboard", "clear_content"],
      ["clearTimelineClipboardHistory", "clear_history"],
    ]) {
      runtimeClient[method] = async (
        requestedProductionId,
        request,
      ) => {
        runtimeCalls.push({
          method,
          requestedProductionId,
          request: structuredClone(request),
        });
        const response = makeClipboardResponse(
          productionId,
          sessionId,
          operation,
          request.expected_revision,
        );
        activeSnapshot = response.snapshot;
        return response;
      };
    }

    const runtime = new stateModule.ReviewWorkspaceSessionRuntime(
      runtimeClient,
    );
    await runtime.open(productionId);
    await runtime.copyTimelineClips({
      clip_ids: ["clip_1"],
    });
    const afterCopy = runtime.getState();
    await runtime.pasteTimelineClips({
      at_time: 8.5,
    });
    await runtime.restoreTimelineClipboardHistory({
      entry_id: "history_1",
    });
    await runtime.clearTimelineClipboardHistory();
    await runtime.clearTimelineClipboard();

    const cutWait = deferred();
    runtimeClient.cutTimelineClips = (
      requestedProductionId,
      request,
    ) => {
      runtimeCalls.push({
        method: "cutTimelineClips",
        requestedProductionId,
        request: structuredClone(request),
      });
      return cutWait.promise;
    };
    const beforePending = runtime.getState();
    const pendingCut = runtime.cutTimelineClips({
      clip_ids: ["clip_1"],
    });
    const pendingState = runtime.getState();
    const pendingResponse = makeClipboardResponse(
      productionId,
      sessionId,
      "cut",
      beforePending.snapshot.timeline.revision,
    );
    activeSnapshot = pendingResponse.snapshot;
    cutWait.resolve(pendingResponse);
    await pendingCut;
    const afterCut = runtime.getState();

    const conflictSnapshot = makeSnapshot(
      productionId,
      sessionId,
      afterCut.snapshot.timeline.revision + 2,
      1,
    );
    runtimeClient.copyTimelineClips = async () => {
      activeSnapshot = conflictSnapshot;
      throw new api.ReviewWorkspaceAPIError(
        "Revision conflict.",
        {
          code: "review_session_conflict",
          status: 409,
          productionId,
          sessionId,
          metadata: {
            application_error: {
              expected_revision:
                afterCut.snapshot.timeline.revision,
              current_revision:
                conflictSnapshot.timeline.revision,
            },
          },
        },
      );
    };
    await assert.rejects(
      runtime.copyTimelineClips({
        clip_ids: ["clip_1"],
      }),
    );
    const recovered = runtime.getState();

    const staleWait = deferred();
    runtimeClient.copyTimelineClips = () =>
      staleWait.promise;
    const staleRequest = runtime.copyTimelineClips({
      clip_ids: ["clip_1"],
    });
    runtime.clear();
    staleWait.resolve(
      makeClipboardResponse(
        productionId,
        sessionId,
        "copy",
        conflictSnapshot.timeline.revision,
      ),
    );
    await staleRequest;
    const staleIgnored = runtime.getState();

    const checks = {
      clipboard_contract_exported:
        api.REVIEW_CLIPBOARD_API_CONTRACT_VERSION === "16.4.8",
      request_count_valid: requests.length === 6,
      methods_valid:
        requests.map((item) => item.method).join(",") ===
        "POST,POST,POST,POST,DELETE,DELETE",
      paths_valid:
        requests.every((item) =>
          item.url.includes("/review/clipboard"),
        ),
      copy_body_normalized:
        JSON.stringify(requests[0].body.clip_ids) ===
        JSON.stringify(["clip_1", "clip_2"]),
      paste_body_normalized:
        requests[2].body.target_track_id === "video_overlay" &&
        requests[2].body.track_mapping.video === "video_overlay",
      abort_signal_forwarded:
        requests[0].signal === controller.signal,
      invalid_clip_ids_blocked: invalidClipIdsBlocked,
      invalid_time_blocked: invalidTimeBlocked,
      validation_read_only: requests.length === 6,
      runtime_actions_complete: runtimeCalls.length >= 6,
      runtime_owns_context:
        runtimeCalls.every(
          (call) =>
            call.request.session_id === sessionId &&
            Number.isInteger(call.request.expected_revision),
        ),
      copy_keeps_revision:
        afterCopy.snapshot.timeline.revision === 1,
      pending_state_visible:
        pendingState.pendingOperation === "clipboard_command" &&
        pendingState.pendingClipboardOperation === "cut",
      no_optimistic_timeline_mutation:
        pendingState.snapshot.timeline.revision ===
        beforePending.snapshot.timeline.revision,
      cut_updates_authoritative_snapshot:
        afterCut.lastClipboardOperation === "cut" &&
        afterCut.snapshot.timeline.revision ===
        beforePending.snapshot.timeline.revision + 1,
      revision_conflict_recovered:
        recovered.status === "ready" &&
        recovered.error.isRevisionConflict === true &&
        recovered.snapshot.timeline.revision ===
        conflictSnapshot.timeline.revision,
      stale_response_ignored:
        staleIgnored.status === "idle" &&
        staleIgnored.snapshot === null &&
        staleIgnored.lastClipboardResponse === null,
      state_snapshots_isolated: (() => {
        const state = recovered;
        state.snapshot.timeline.revision = 999;
        return (
          runtime.getState().snapshot === null ||
          runtime.getState().snapshot.timeline.revision !== 999
        );
      })(),
    };

    for (const [name, passed] of Object.entries(checks)) {
      assert.equal(passed, true, `${name} failed`);
    }

    console.log(
      "=== Frontend Clipboard API Client & State Runtime ===",
    );
    for (const [name, passed] of Object.entries(checks)) {
      console.log(`${name}: ${passed}`);
    }
    console.log(
      "\nDONE: Frontend Clipboard API client and state runtime test completed.",
    );
  } finally {
    fs.rmSync(outputRoot, {
      recursive: true,
      force: true,
    });
  }
}


main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
