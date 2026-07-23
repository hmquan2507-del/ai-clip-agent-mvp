/* eslint-disable @typescript-eslint/no-require-imports */
const assert =
  require("node:assert/strict");
const fs =
  require("node:fs");
const path =
  require("node:path");
const ts =
  require("typescript");


require.extensions[".ts"] =
  function compileTypeScript(
    module,
    filename,
  ) {
    const source =
      fs.readFileSync(
        filename,
        "utf8",
      );

    const output =
      ts.transpileModule(
        source,
        {
          fileName: filename,
          compilerOptions: {
            target:
              ts.ScriptTarget.ES2022,
            module:
              ts.ModuleKind.CommonJS,
            moduleResolution:
              ts.ModuleResolutionKind
                .NodeJs,
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
    (
      "../src/features/review/"
      + "api/index.ts"
    ),
  ),
);


const productionId =
  "221e4b01-5fb9-4b4a-a549-4fb32c455059";

const sessionId = "session-1";


function successResponse(
  operation,
  extra = {},
) {
  return new Response(
    JSON.stringify({
      contract_version:
        "16.2.3",
      success: true,
      operation,
      production_id:
        productionId,
      session_id:
        sessionId,
      metadata: {},
      ...extra,
    }),
    {
      status: 200,
      headers: {
        "Content-Type":
          "application/json",
      },
    },
  );
}


function buildSuccessFetcher(
  calls,
) {
  return async (
    url,
    init,
  ) => {
    calls.push({
      url,
      init,
    });

    if (
      init.method === "DELETE"
    ) {
      return successResponse(
        "close_session",
        {
          state: {},
          event: null,
        },
      );
    }

    if (
      url.includes("/reset")
    ) {
      return successResponse(
        "reset_session",
        {
          snapshot: {},
        },
      );
    }

    if (
      url.includes("/snapshot")
    ) {
      return successResponse(
        "get_snapshot",
        {
          snapshot: {},
        },
      );
    }

    if (
      init.method === "GET"
    ) {
      return successResponse(
        "get_session",
        {
          session: {},
          snapshot: {},
        },
      );
    }

    return successResponse(
      "open_session",
      {
        session: {},
        snapshot: {},
      },
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
      fetch:
        buildSuccessFetcher(
          calls,
        ),
    });

  await client.openSession(
    productionId,
  );

  await client.getSession(
    productionId,
    sessionId,
  );

  await client.getSnapshot(
    productionId,
    sessionId,
    {
      signal:
        abortController.signal,
    },
  );

  await client.resetSession(
    productionId,
    {
      session_id: sessionId,
    },
  );

  await client.closeSession(
    productionId,
    {
      session_id: sessionId,
    },
  );

  const requestCountValid =
    calls.length === 5;

  const baseUrlNormalized =
    client.baseUrl ===
    "http://localhost:8000/api/v1";

  const openPayload =
    JSON.parse(
      calls[0].init.body,
    );

  const openBodyValid =
    openPayload.force_refresh ===
      false &&
    openPayload.replace_existing ===
      false;

  const sessionQueryValid =
    calls[1].url.endsWith(
      (
        "/session?session_id="
        + "session-1"
      ),
    );

  const snapshotQueryValid =
    calls[2].url.endsWith(
      (
        "/snapshot?session_id="
        + "session-1"
      ),
    );

  const abortSignalForwarded =
    calls[2].init.signal ===
    abortController.signal;

  const resetBodyValid =
    JSON.parse(
      calls[3].init.body,
    ).session_id === sessionId;

  const closeBodyValid =
    calls[4].init.method ===
      "DELETE" &&
    JSON.parse(
      calls[4].init.body,
    ).session_id === sessionId;

  const headersValid =
    calls[0].init.headers.get(
      "Accept",
    ) === "application/json" &&
    calls[0].init.headers.get(
      "Content-Type",
    ) === "application/json";

  let invalidRefreshBlocked =
    false;

  try {
    await client.openSession(
      productionId,
      {
        force_refresh: true,
      },
    );
  } catch (error) {
    invalidRefreshBlocked =
      error instanceof
        ReviewWorkspaceAPIError &&
      error.code ===
        (
          "review_request_"
          + "validation_failed"
        ) &&
      error.status === 422;
  }

  const apiErrorClient =
    new ReviewWorkspaceClient({
      fetch: async () =>
        new Response(
          JSON.stringify({
            contract_version:
              "16.2.3",
            success: false,
            error: {
              code:
                "review_session_not_found",
              message:
                (
                  "Không tìm thấy phiên "
                  + "review đang hoạt động."
                ),
              technical_message:
                "Missing session.",
              production_id:
                productionId,
              session_id:
                sessionId,
              metadata: {},
            },
          }),
          {
            status: 404,
          },
        ),
    });

  let apiErrorParsed = false;

  try {
    await apiErrorClient
      .getSnapshot(
        productionId,
        sessionId,
      );
  } catch (error) {
    apiErrorParsed =
      error instanceof
        ReviewWorkspaceAPIError &&
      error.code ===
        "review_session_not_found" &&
      error.status === 404 &&
      error.sessionId ===
        sessionId;
  }

  const invalidContractClient =
    new ReviewWorkspaceClient({
      fetch: async () =>
        new Response(
          JSON.stringify({
            contract_version:
              "old-version",
            success: true,
            operation:
              "get_snapshot",
            production_id:
              productionId,
            session_id:
              sessionId,
            metadata: {},
            snapshot: {},
          }),
          {
            status: 200,
          },
        ),
    });

  let invalidContractBlocked =
    false;

  try {
    await invalidContractClient
      .getSnapshot(
        productionId,
        sessionId,
      );
  } catch (error) {
    invalidContractBlocked =
      error instanceof
        ReviewWorkspaceAPIError &&
      error.code ===
        "invalid_response";
  }

  const networkClient =
    new ReviewWorkspaceClient({
      fetch: async () => {
        throw new TypeError(
          "Network unavailable",
        );
      },
    });

  let networkErrorMapped = false;

  try {
    await networkClient
      .openSession(
        productionId,
      );
  } catch (error) {
    networkErrorMapped =
      error instanceof
        ReviewWorkspaceAPIError &&
      error.code ===
        "network_error" &&
      error.status === 0;
  }

  const checks = {
    request_count_valid:
      requestCountValid,
    base_url_normalized:
      baseUrlNormalized,
    open_body_valid:
      openBodyValid,
    session_query_valid:
      sessionQueryValid,
    snapshot_query_valid:
      snapshotQueryValid,
    abort_signal_forwarded:
      abortSignalForwarded,
    reset_body_valid:
      resetBodyValid,
    close_body_valid:
      closeBodyValid,
    headers_valid:
      headersValid,
    invalid_refresh_blocked:
      invalidRefreshBlocked,
    api_error_parsed:
      apiErrorParsed,
    invalid_contract_blocked:
      invalidContractBlocked,
    network_error_mapped:
      networkErrorMapped,
  };

  console.log(
    "=== Frontend Review "
    + "API Client ===",
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
    Object.values(
      checks,
    ).every(Boolean),
    checks,
  );

  console.log(
    (
      "\nDONE: Frontend Review "
      + "API client test completed."
    ),
  );
}


main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});