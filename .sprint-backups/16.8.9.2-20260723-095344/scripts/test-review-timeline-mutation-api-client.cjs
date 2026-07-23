/* eslint-disable @typescript-eslint/no-require-imports */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const ts = require("typescript");

require.extensions[".ts"] = function compileTypeScript(
  module,
  filename,
) {
  const source = fs.readFileSync(
    filename,
    "utf8",
  );

  const output = ts.transpileModule(
    source,
    {
      fileName: filename,
      compilerOptions: {
        target: ts.ScriptTarget.ES2022,
        module: ts.ModuleKind.CommonJS,
        moduleResolution:
          ts.ModuleResolutionKind.NodeJs,
        esModuleInterop: true,
      },
    },
  );

  module._compile(
    output.outputText,
    filename,
  );
};

const {
  ReviewWorkspaceAPIError,
  ReviewWorkspaceClient,
} = require(
  path.resolve(
    __dirname,
    "../src/features/review/api/index.ts",
  ),
);

const productionId =
  "221e4b01-5fb9-4b4a-a549-4fb32c455059";
const sessionId = "session-1";

const operationByPath = {
  "/timeline/move": "move_clip",
  "/timeline/trim-start": "trim_clip_start",
  "/timeline/trim-end": "trim_clip_end",
  "/timeline/split": "split_clip",
  "/timeline/duplicate": "duplicate_clip",
  "/timeline/delete": "delete_clip",
  "/timeline/close-gap": "close_gap",
  "/timeline/undo": "undo",
  "/timeline/redo": "redo",
};

function timelineResponse(operation) {
  return new Response(
    JSON.stringify({
      contract_version: "16.4.1",
      success: true,
      operation,
      production_id: productionId,
      session_id: sessionId,
      snapshot: {
        session: {},
        timeline: {
          revision: 2,
        },
      },
      command: {
        command_id: "command-1",
      },
      event: {
        action: "execute",
      },
      history: {
        can_undo: true,
        can_redo: false,
      },
      metadata: {
        previous_revision: 1,
        current_revision: 2,
      },
    }),
    {
      status: 200,
      headers: {
        "Content-Type": "application/json",
      },
    },
  );
}

function buildFetcher(calls) {
  return async (url, init) => {
    calls.push({ url, init });

    const pathname = new URL(url).pathname;
    const matchingPath =
      Object.keys(operationByPath).find(
        (item) =>
          pathname.endsWith(item),
      );

    assert.ok(matchingPath);

    return timelineResponse(
      operationByPath[matchingPath],
    );
  };
}

async function main() {
  const calls = [];
  const abortController =
    new AbortController();

  const client =
    new ReviewWorkspaceClient({
      baseUrl:
        "http://localhost:8000/api/v1/",
      fetch: buildFetcher(calls),
    });

  await client.moveClip(
    productionId,
    {
      session_id: sessionId,
      expected_revision: 1,
      clip_id: "clip-1",
      new_start_time: 2,
      target_track_id:
        "track-video",
    },
  );

  await client.trimClipStart(
    productionId,
    {
      session_id: sessionId,
      clip_id: "clip-1",
      new_start_time: 1,
    },
  );

  await client.trimClipEnd(
    productionId,
    {
      session_id: sessionId,
      clip_id: "clip-1",
      new_end_time: 4,
    },
  );

  await client.splitClip(
    productionId,
    {
      session_id: sessionId,
      clip_id: "clip-1",
      split_time: 2,
      right_clip_id:
        "clip-right",
    },
  );

  await client.duplicateClip(
    productionId,
    {
      session_id: sessionId,
      clip_id: "clip-1",
      new_clip_id:
        "clip-copy",
      new_start_time: 5,
      target_track_id:
        "track-video",
    },
  );

  await client.deleteClip(
    productionId,
    {
      session_id: sessionId,
      clip_id: "clip-copy",
      close_gap: true,
    },
  );

  await client.closeGap(
    productionId,
    {
      session_id: sessionId,
      track_id: "track-video",
      gap_start: 4,
      gap_end: 5,
    },
  );

  await client.undoTimeline(
    productionId,
    {
      session_id: sessionId,
    },
  );

  await client.redoTimeline(
    productionId,
    {
      session_id: sessionId,
    },
    {
      signal:
        abortController.signal,
    },
  );

  const requestCountValid =
    calls.length === 9;

  const methodsValid =
    calls.every(
      (call) =>
        call.init.method === "POST",
    );

  const pathsValid =
    calls.every((call) => {
      const pathname =
        new URL(call.url).pathname;

      return Object.keys(
        operationByPath,
      ).some((item) =>
        pathname.endsWith(item),
      );
    });

  const moveBody =
    JSON.parse(calls[0].init.body);

  const moveBodyValid =
    moveBody.session_id ===
      sessionId &&
    moveBody.expected_revision ===
      1 &&
    moveBody.clip_id ===
      "clip-1" &&
    moveBody.new_start_time ===
      2 &&
    moveBody.target_track_id ===
      "track-video";

  const deleteBody =
    JSON.parse(calls[5].init.body);

  const deleteBodyValid =
    deleteBody.close_gap === true;

  const closeGapBody =
    JSON.parse(calls[6].init.body);

  const closeGapBodyValid =
    closeGapBody.gap_start === 4 &&
    closeGapBody.gap_end === 5;

  const abortSignalForwarded =
    calls[8].init.signal ===
    abortController.signal;

  const headersValid =
    calls[0].init.headers.get(
      "Accept",
    ) === "application/json" &&
    calls[0].init.headers.get(
      "Content-Type",
    ) === "application/json";

  const callsBeforeValidation =
    calls.length;

  let invalidTimeBlocked = false;

  try {
    await client.moveClip(
      productionId,
      {
        session_id: sessionId,
        clip_id: "clip-1",
        new_start_time: -1,
      },
    );
  } catch (error) {
    invalidTimeBlocked =
      error instanceof
        ReviewWorkspaceAPIError &&
      error.status === 422;
  }

  const validationReadOnly =
    calls.length ===
    callsBeforeValidation;

  let invalidRevisionBlocked = false;

  try {
    await client.undoTimeline(
      productionId,
      {
        session_id: sessionId,
        expected_revision: 0,
      },
    );
  } catch (error) {
    invalidRevisionBlocked =
      error instanceof
        ReviewWorkspaceAPIError &&
      error.status === 422;
  }

  const conflictClient =
    new ReviewWorkspaceClient({
      fetch: async () =>
        new Response(
          JSON.stringify({
            contract_version:
              "16.2.3",
            success: false,
            error: {
              code:
                "review_session_conflict",
              message:
                "Revision conflict.",
              technical_message:
                "Expected 4, current 5.",
              production_id:
                productionId,
              session_id:
                sessionId,
              metadata: {
                application_error: {
                  expected_revision: 4,
                  current_revision: 5,
                },
              },
            },
          }),
          {
            status: 409,
          },
        ),
    });

  let revisionConflictMapped =
    false;

  try {
    await conflictClient.undoTimeline(
      productionId,
      {
        session_id: sessionId,
        expected_revision: 4,
      },
    );
  } catch (error) {
    revisionConflictMapped =
      error instanceof
        ReviewWorkspaceAPIError &&
      error.isRevisionConflict &&
      error.expectedRevision === 4 &&
      error.currentRevision === 5;
  }

  const invalidContractClient =
    new ReviewWorkspaceClient({
      fetch: async () =>
        timelineResponse(
          "move_clip",
        ).json().then(
          (payload) =>
            new Response(
              JSON.stringify({
                ...payload,
                contract_version:
                  "16.2.3",
              }),
              {
                status: 200,
              },
            ),
        ),
    });

  let invalidContractBlocked =
    false;

  try {
    await invalidContractClient
      .moveClip(
        productionId,
        {
          session_id: sessionId,
          clip_id: "clip-1",
          new_start_time: 1,
        },
      );
  } catch (error) {
    invalidContractBlocked =
      error instanceof
        ReviewWorkspaceAPIError &&
      error.code ===
        "invalid_response";
  }

  const checks = {
    request_count_valid:
      requestCountValid,
    methods_valid:
      methodsValid,
    paths_valid:
      pathsValid,
    move_body_valid:
      moveBodyValid,
    delete_body_valid:
      deleteBodyValid,
    close_gap_body_valid:
      closeGapBodyValid,
    abort_signal_forwarded:
      abortSignalForwarded,
    headers_valid:
      headersValid,
    invalid_time_blocked:
      invalidTimeBlocked,
    invalid_revision_blocked:
      invalidRevisionBlocked,
    validation_read_only:
      validationReadOnly,
    revision_conflict_mapped:
      revisionConflictMapped,
    invalid_contract_blocked:
      invalidContractBlocked,
  };

  console.log(
    "=== Frontend Timeline "
    + "Mutation API Client ===",
  );

  for (
    const [name, passed]
    of Object.entries(checks)
  ) {
    console.log(
      `${name}: ${passed}`,
    );
  }

  assert.ok(
    Object.values(checks).every(
      Boolean,
    ),
    checks,
  );

  console.log(
    "\nDONE: Frontend timeline "
    + "mutation API client test "
    + "completed.",
  );
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});