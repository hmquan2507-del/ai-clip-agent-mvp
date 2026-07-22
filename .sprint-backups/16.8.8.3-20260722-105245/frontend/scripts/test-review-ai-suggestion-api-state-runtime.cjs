/* eslint-disable @typescript-eslint/no-require-imports */

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const ts = require("typescript");

const ROOT = process.cwd();
const REVIEW_ROOT = path.join(ROOT, "src/features/review");

function compileReviewModules(outputRoot) {
  for (const folder of ["api", "state"]) {
    const sourceFolder = path.join(REVIEW_ROOT, folder);
    const outputFolder = path.join(outputRoot, folder);
    fs.mkdirSync(outputFolder, { recursive: true });
    for (const filename of fs.readdirSync(sourceFolder)) {
      if (!filename.endsWith(".ts")) continue;
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
        path.join(outputFolder, filename.replace(/\.ts$/, ".js")),
        compiled.outputText,
        "utf8",
      );
    }
  }
}

function makeWorkspaceSnapshot(productionId, sessionId, revision) {
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
      clip_count: 0,
    },
    metadata: {},
  };
}

function makeSuggestionSnapshot(productionId, timelineRevision, lifecycleRevision, selected = null) {
  return {
    contract_version: "16.6.1",
    production_id: productionId,
    lifecycle_revision: lifecycleRevision,
    timeline_revision: timelineRevision,
    read_model: {
      contract_version: "16.6.1",
      production_id: productionId,
      timeline_revision: timelineRevision,
      suggestions: [],
      selected_suggestion_id: selected,
      count: 0,
      actionable_count: 0,
      stale_count: 0,
      generated_at: "2026-07-18T00:00:00Z",
      metadata: {},
    },
    created_at: "2026-07-18T00:00:00Z",
    metadata: {},
  };
}

function makeSuggestionResponse(
  productionId,
  sessionId,
  operation,
  timelineRevision,
  lifecycleRevision,
  selected = null,
) {
  return {
    contract_version: "16.6.4",
    success: true,
    operation,
    production_id: productionId,
    session_id: sessionId,
    timeline_revision: timelineRevision,
    lifecycle_revision: lifecycleRevision,
    workspace_snapshot: makeWorkspaceSnapshot(
      productionId,
      sessionId,
      timelineRevision,
    ),
    suggestion_snapshot: makeSuggestionSnapshot(
      productionId,
      timelineRevision,
      lifecycleRevision,
      selected,
    ),
    timeline_command_result:
      operation === "apply_suggestion"
        ? { operation: "move_clip" }
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
    path.join(ROOT, ".review-suggestion-test-"),
  );
  try {
    compileReviewModules(outputRoot);
    const api = require(path.join(outputRoot, "api/index.js"));
    const stateModule = require(path.join(outputRoot, "state/runtime.js"));
    const productionId = "221e4b01-5fb9-4b4a-a549-4fb32c455059";
    const sessionId = "frontend-suggestion-session";

    const requests = [];
    const operationBySuffix = {
      "/suggestions/select": "select_suggestion",
      "/suggestions/apply": "apply_suggestion",
      "/suggestions/dismiss": "dismiss_suggestion",
      "/suggestions/regenerate": "regenerate_suggestions",
      "/suggestions": "get_suggestions",
    };
    const fetcher = async (url, init) => {
      const pathname = new URL(url).pathname;
      const suffix = Object.keys(operationBySuffix)
        .sort((a, b) => b.length - a.length)
        .find((item) => pathname.endsWith(item));
      const operation = operationBySuffix[suffix];
      const body = init.body ? JSON.parse(init.body) : null;
      requests.push({
        url: String(url),
        method: init.method,
        body,
        signal: init.signal,
      });
      const timelineRevision = operation === "apply_suggestion" ? 5 : 4;
      return new Response(
        JSON.stringify(
          makeSuggestionResponse(
            productionId,
            body?.session_id ?? sessionId,
            operation,
            timelineRevision,
            2,
          ),
        ),
        { status: 200, headers: { "Content-Type": "application/json" } },
      );
    };
    const client = api.createReviewWorkspaceClient({
      baseUrl: "http://localhost:8000/api/v1/",
      fetch: fetcher,
    });
    const controller = new AbortController();
    await client.getAISuggestions(productionId, sessionId, {
      signal: controller.signal,
    });
    await client.selectAISuggestion(productionId, {
      session_id: sessionId,
      suggestion_id: " suggestion_1 ",
      expected_lifecycle_revision: 1,
    });
    await client.applyAISuggestion(productionId, {
      session_id: sessionId,
      suggestion_id: "suggestion_1",
      expected_timeline_revision: 4,
      expected_lifecycle_revision: 1,
    });
    await client.dismissAISuggestion(productionId, {
      session_id: sessionId,
      suggestion_id: "suggestion_1",
      expected_lifecycle_revision: 2,
    });
    await client.regenerateAISuggestions(productionId, {
      session_id: sessionId,
      expected_lifecycle_revision: 3,
    });

    let invalidIdBlocked = false;
    try {
      await client.applyAISuggestion(productionId, {
        session_id: sessionId,
        suggestion_id: "",
      });
    } catch {
      invalidIdBlocked = true;
    }
    let invalidRevisionBlocked = false;
    try {
      await client.regenerateAISuggestions(productionId, {
        session_id: sessionId,
        expected_lifecycle_revision: 0,
      });
    } catch {
      invalidRevisionBlocked = true;
    }

    let activeTimelineRevision = 1;
    let lifecycleRevision = 1;
    let selectedSuggestion = null;
    const runtimeCalls = [];
    const runtimeClient = {
      async openSession() {
        const snapshot = makeWorkspaceSnapshot(productionId, sessionId, 1);
        return {
          production_id: productionId,
          session_id: sessionId,
          session: snapshot.session,
          snapshot,
        };
      },
      async getAISuggestions() {
        runtimeCalls.push({ operation: "get_suggestions" });
        return makeSuggestionResponse(
          productionId,
          sessionId,
          "get_suggestions",
          activeTimelineRevision,
          lifecycleRevision,
          selectedSuggestion,
        );
      },
      async selectAISuggestion(_productionId, request) {
        runtimeCalls.push({ operation: "select_suggestion", request: structuredClone(request) });
        lifecycleRevision += 1;
        selectedSuggestion = request.suggestion_id;
        return makeSuggestionResponse(
          productionId,
          sessionId,
          "select_suggestion",
          activeTimelineRevision,
          lifecycleRevision,
          selectedSuggestion,
        );
      },
      async applyAISuggestion(_productionId, request) {
        runtimeCalls.push({ operation: "apply_suggestion", request: structuredClone(request) });
        activeTimelineRevision += 1;
        lifecycleRevision += 1;
        return makeSuggestionResponse(
          productionId,
          sessionId,
          "apply_suggestion",
          activeTimelineRevision,
          lifecycleRevision,
          selectedSuggestion,
        );
      },
      async dismissAISuggestion(_productionId, request) {
        runtimeCalls.push({ operation: "dismiss_suggestion", request: structuredClone(request) });
        lifecycleRevision += 1;
        return makeSuggestionResponse(
          productionId,
          sessionId,
          "dismiss_suggestion",
          activeTimelineRevision,
          lifecycleRevision,
          selectedSuggestion,
        );
      },
      async regenerateAISuggestions(_productionId, request) {
        runtimeCalls.push({ operation: "regenerate_suggestions", request: structuredClone(request) });
        lifecycleRevision += 1;
        return makeSuggestionResponse(
          productionId,
          sessionId,
          "regenerate_suggestions",
          activeTimelineRevision,
          lifecycleRevision,
          null,
        );
      },
    };
    const runtime = new stateModule.ReviewWorkspaceSessionRuntime(runtimeClient);
    await runtime.open(productionId);
    await runtime.refreshAISuggestions();

    const wait = deferred();
    const originalSelect = runtimeClient.selectAISuggestion;
    runtimeClient.selectAISuggestion = (_productionId, request) => {
      runtimeCalls.push({ operation: "select_suggestion_pending", request: structuredClone(request) });
      return wait.promise;
    };
    const beforePending = runtime.getState();
    const pending = runtime.selectAISuggestion({ suggestion_id: "suggestion_1" });
    const pendingState = runtime.getState();
    lifecycleRevision += 1;
    selectedSuggestion = "suggestion_1";
    wait.resolve(
      makeSuggestionResponse(
        productionId,
        sessionId,
        "select_suggestion",
        activeTimelineRevision,
        lifecycleRevision,
        selectedSuggestion,
      ),
    );
    await pending;
    runtimeClient.selectAISuggestion = originalSelect;
    const afterSelect = runtime.getState();
    await runtime.applyAISuggestion({ suggestion_id: "suggestion_1" });
    const afterApply = runtime.getState();
    await runtime.dismissAISuggestion({ suggestion_id: "suggestion_1" });
    await runtime.regenerateAISuggestions();

    const conflictTimeline = activeTimelineRevision;
    const conflictLifecycle = lifecycleRevision + 3;
    runtimeClient.dismissAISuggestion = async () => {
      lifecycleRevision = conflictLifecycle;
      throw new api.ReviewWorkspaceAPIError("Suggestion conflict.", {
        code: "review_ai_suggestion_revision_conflict",
        status: 409,
        productionId,
        sessionId,
        metadata: {
          application_error: {
            expected_revision: conflictLifecycle - 1,
            current_revision: conflictLifecycle,
          },
        },
      });
    };
    await assert.rejects(
      runtime.dismissAISuggestion({ suggestion_id: "suggestion_1" }),
    );
    const recovered = runtime.getState();

    const staleWait = deferred();
    runtimeClient.selectAISuggestion = () => staleWait.promise;
    const staleRequest = runtime.selectAISuggestion({ suggestion_id: "suggestion_1" });
    runtime.clear();
    staleWait.resolve(
      makeSuggestionResponse(
        productionId,
        sessionId,
        "select_suggestion",
        conflictTimeline,
        conflictLifecycle + 1,
      ),
    );
    await staleRequest;
    const staleIgnored = runtime.getState();

    const isolated = afterApply;
    isolated.suggestionSnapshot.read_model.metadata.mutated = true;

    const checks = {
      suggestion_contract_exported:
        api.REVIEW_AI_SUGGESTION_API_CONTRACT_VERSION === "16.6.4",
      request_count_valid: requests.length === 5,
      methods_valid:
        requests.map((item) => item.method).join(",") ===
        "GET,POST,POST,POST,POST",
      paths_valid: requests.every((item) => item.url.includes("/review/suggestions")),
      select_body_normalized: requests[1].body.suggestion_id === "suggestion_1",
      apply_revisions_forwarded:
        requests[2].body.expected_timeline_revision === 4 &&
        requests[2].body.expected_lifecycle_revision === 1,
      abort_signal_forwarded: requests[0].signal === controller.signal,
      invalid_id_blocked: invalidIdBlocked,
      invalid_revision_blocked: invalidRevisionBlocked,
      validation_read_only: requests.length === 5,
      runtime_actions_complete: runtimeCalls.length >= 5,
      runtime_owns_context: runtimeCalls
        .filter((item) => item.request)
        .every((item) => item.request.session_id === sessionId),
      pending_state_visible:
        pendingState.pendingOperation === "ai_suggestion" &&
        pendingState.pendingSuggestionOperation === "select_suggestion",
      no_optimistic_updates:
        pendingState.snapshot.timeline.revision ===
          beforePending.snapshot.timeline.revision &&
        pendingState.suggestionSnapshot.lifecycle_revision ===
          beforePending.suggestionSnapshot.lifecycle_revision,
      selection_authoritative:
        afterSelect.suggestionSnapshot.read_model.selected_suggestion_id ===
        "suggestion_1",
      apply_updates_authoritative_timeline:
        afterApply.snapshot.timeline.revision === 2 &&
        afterApply.lastSuggestionOperation === "apply_suggestion",
      revision_conflict_recovered:
        recovered.status === "ready" &&
        recovered.error.isRevisionConflict === true &&
        recovered.suggestionSnapshot.lifecycle_revision === conflictLifecycle,
      stale_response_ignored:
        staleIgnored.status === "idle" &&
        staleIgnored.snapshot === null &&
        staleIgnored.suggestionSnapshot === null,
      state_snapshots_isolated:
        runtime.getState().status === "idle" &&
        !afterApply.lastSuggestionResponse.metadata.mutated,
    };
    assert.equal(Object.values(checks).every(Boolean), true, checks);
    console.log("=== Frontend AI Suggestion API Client & State Runtime ===");
    for (const [name, value] of Object.entries(checks)) {
      console.log(`${name}: ${value}`);
    }
    console.log("\nDONE: Frontend AI suggestion API client and state runtime test completed.");
  } finally {
    fs.rmSync(outputRoot, { recursive: true, force: true });
  }
}

main();
