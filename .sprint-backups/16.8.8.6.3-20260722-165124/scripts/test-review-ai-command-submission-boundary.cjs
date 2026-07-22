/* eslint-disable @typescript-eslint/no-require-imports */

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const ts = require("typescript");

require.extensions[".ts"] = function compileTypeScript(module, filename) {
  const source = fs.readFileSync(filename, "utf8");
  const output = ts.transpileModule(source, {
    fileName: filename,
    compilerOptions: {
      target: ts.ScriptTarget.ES2022,
      module: ts.ModuleKind.CommonJS,
      moduleResolution: ts.ModuleResolutionKind.NodeJs,
      esModuleInterop: true,
      jsx: ts.JsxEmit.ReactJSX,
    },
  });
  module._compile(output.outputText, filename);
};

const ROOT = process.cwd();
const REVIEW_ROOT = path.join(ROOT, "src/features/review");
const api = require(path.join(REVIEW_ROOT, "api/index.ts"));
const state = require(path.join(REVIEW_ROOT, "state/index.ts"));

const productionId = "221e4b01-5fb9-4b4a-a549-4fb32c455059";
const sessionId = "command-boundary-session";

function session(revision = 4) {
  return {
    session_id: sessionId,
    production_id: productionId,
    status: "ready",
    active: true,
    ready: true,
    closed: false,
    timeline_revision: revision,
    dirty: false,
    revision,
    created_at: "2026-07-18T00:00:00.000Z",
    updated_at: "2026-07-18T00:00:00.000Z",
    closed_at: null,
    error: null,
    metadata: {},
  };
}

function snapshot(revision = 4) {
  return {
    session: session(revision),
    workspace: { production_id: productionId, metadata: {} },
    timeline: {
      production_id: productionId,
      revision,
      tracks: [],
      metadata: { marker: `revision-${revision}` },
    },
    preview: {},
    selection: {},
    history: {},
    clipboard: {},
    created_at: "2026-07-18T00:00:00.000Z",
    consistency: {
      production_ids_match: true,
      workspace_timeline_consistent: true,
    },
    metadata: {},
  };
}

function submissionResponse(commandText = "Làm hook mạnh hơn") {
  return {
    contract_version: "16.6.8",
    success: true,
    operation: "submit_command",
    production_id: productionId,
    session_id: sessionId,
    timeline_revision: 4,
    submission: {
      contract_version: "16.6.8",
      submission_id: "command-submission-1",
      production_id: productionId,
      session_id: sessionId,
      command_text: commandText,
      timeline_revision: 4,
      status: "accepted",
      client_request_id: "client-command-1",
      created_at: "2026-07-18T00:00:01.000Z",
      metadata: {
        execution_authorized: false,
        proposal_created: false,
      },
    },
    duplicate: false,
    timeline_mutated: false,
  };
}

function deferred() {
  let resolve;
  const promise = new Promise((yes) => { resolve = yes; });
  return { promise, resolve };
}

async function main() {
  const requests = [];
  const controller = new AbortController();
  const client = api.createReviewWorkspaceClient({
    baseUrl: "http://localhost:8000/api/v1/",
    fetch: async (url, init) => {
      requests.push({
        url: String(url),
        method: init.method,
        body: JSON.parse(init.body),
        signal: init.signal,
        headers: new Headers(init.headers),
      });
      return new Response(JSON.stringify(submissionResponse()), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    },
  });

  await client.submitAICommand(
    productionId,
    {
      session_id: sessionId,
      command_text: "  Làm   hook mạnh hơn  ",
      expected_timeline_revision: 4,
      client_request_id: "client-command-1",
    },
    { signal: controller.signal },
  );

  let invalidCommandBlocked = false;
  try {
    await client.submitAICommand(productionId, {
      session_id: sessionId,
      command_text: "   ",
    });
  } catch {
    invalidCommandBlocked = true;
  }

  const wait = deferred();
  const runtimeCalls = [];
  const runtimeClient = {
    async openSession() {
      return {
        contract_version: "16.2.3",
        success: true,
        operation: "open_session",
        production_id: productionId,
        session_id: sessionId,
        session: session(),
        snapshot: snapshot(),
        metadata: {},
      };
    },
    submitAICommand(currentProductionId, request, options) {
      runtimeCalls.push({
        productionId: currentProductionId,
        request: structuredClone(request),
        signal: options.signal,
      });
      return wait.promise;
    },
  };
  const runtime = state.createReviewWorkspaceSessionRuntime({
    client: runtimeClient,
  });
  await runtime.open(productionId);
  const before = runtime.getState();
  const pendingPromise = runtime.submitAICommand({
    command_text: "  Thêm   B-roll sản phẩm ",
    client_request_id: "client-command-1",
  });
  const pending = runtime.getState();
  wait.resolve(submissionResponse("Thêm B-roll sản phẩm"));
  await pendingPromise;
  const completed = runtime.getState();

  const isolated = completed;
  isolated.lastAICommandSubmission.submission.metadata.mutated = true;

  const providerSource = fs.readFileSync(
    path.join(REVIEW_ROOT, "react/provider.tsx"), "utf8",
  );
  const workspaceSource = fs.readFileSync(
    path.join(REVIEW_ROOT, "integration/runtime-workspace.tsx"), "utf8",
  );
  const shellSource = [
    "shell/review-editor-shell.tsx",
    "shell/ai-command-bar.tsx",
  ].map((file) => fs.readFileSync(path.join(REVIEW_ROOT, file), "utf8")).join("\n");

  const checks = {
    command_contract_exported:
      api.REVIEW_AI_COMMAND_API_CONTRACT_VERSION === "16.6.8",
    request_count_valid: requests.length === 1,
    method_and_path_valid:
      requests[0].method === "POST" &&
      requests[0].url.endsWith("/review/commands/submit"),
    command_body_normalized:
      requests[0].body.command_text === "Làm hook mạnh hơn" &&
      requests[0].body.expected_timeline_revision === 4,
    idempotency_key_forwarded:
      requests[0].body.client_request_id === "client-command-1",
    abort_signal_forwarded: requests[0].signal === controller.signal,
    headers_valid:
      requests[0].headers.get("content-type") === "application/json",
    invalid_command_blocked: invalidCommandBlocked,
    validation_read_only: requests.length === 1,
    runtime_owns_context:
      runtimeCalls[0].productionId === productionId &&
      runtimeCalls[0].request.session_id === sessionId &&
      runtimeCalls[0].request.expected_timeline_revision === 4,
    pending_state_visible:
      pending.status === "submitting_command" &&
      pending.pendingOperation === "ai_command_submission" &&
      pending.aiCommandSubmissionPending === true,
    no_optimistic_timeline_update:
      JSON.stringify(pending.snapshot) === JSON.stringify(before.snapshot),
    accepted_response_authoritative:
      completed.lastAICommandSubmission.submission.status === "accepted" &&
      completed.lastAICommandSubmission.timeline_mutated === false,
    timeline_stays_authoritative:
      JSON.stringify(completed.snapshot) === JSON.stringify(before.snapshot),
    response_state_isolated:
      runtime.getState().lastAICommandSubmission.submission.metadata.mutated !== true,
    execution_not_authorized:
      completed.lastAICommandSubmission.submission.metadata.execution_authorized === false,
    provider_delegates_to_runtime:
      providerSource.includes("runtime.submitAICommand"),
    workspace_is_action_boundary:
      workspaceSource.includes("actions.submitAICommand") &&
      workspaceSource.includes("onAICommandSubmit"),
    command_form_connected:
      shellSource.includes("onSubmit={(event) =>") &&
      shellSource.includes("onAICommandSubmit"),
    no_direct_api_or_timeline_mutation:
      !shellSource.includes("fetch(") &&
      !shellSource.includes("/commands/submit") &&
      !shellSource.includes("move_clip("),
  };

  for (const [name, value] of Object.entries(checks)) {
    assert.equal(value, true, `${name} failed`);
  }
  console.log("=== Natural-language Command Submission Boundary ===");
  for (const [name, value] of Object.entries(checks)) {
    console.log(`${name}: ${value}`);
  }
  console.log("\nDONE: Natural-language command submission boundary test completed.");
  runtime.dispose();
}

main();
