import {
  REVIEW_WORKSPACE_API_CONTRACT_VERSION,
  type CloseReviewWorkspaceRequest,
  type OpenReviewWorkspaceRequest,
  type ResetReviewWorkspaceRequest,
  type ReviewWorkspaceAPIOperation,
  type ReviewWorkspaceCloseResponse,
  type ReviewWorkspaceResetResponse,
  type ReviewWorkspaceSessionResponse,
  type ReviewWorkspaceSnapshotResponse,
} from "./contracts";
import { ReviewWorkspaceAPIError } from "./errors";

const DEFAULT_API_BASE_URL = "http://localhost:8000/api/v1";

export interface ReviewWorkspaceRequestOptions {
  signal?: AbortSignal;
}

export interface ReviewWorkspaceClientConfig {
  baseUrl?: string;
  fetch?: typeof fetch;
  headers?: HeadersInit;
}

export class ReviewWorkspaceClient {
  readonly baseUrl: string;

  private readonly fetcher: typeof fetch;
  private readonly headers: HeadersInit;

  constructor(config: ReviewWorkspaceClientConfig = {}) {
    this.baseUrl = normalizeBaseUrl(
      config.baseUrl ??
        process.env.NEXT_PUBLIC_API_BASE_URL ??
        DEFAULT_API_BASE_URL,
    );
    this.fetcher = config.fetch ?? globalThis.fetch.bind(globalThis);
    this.headers = config.headers ?? {};
  }

  openSession(
    productionId: string,
    request: OpenReviewWorkspaceRequest = {},
    options: ReviewWorkspaceRequestOptions = {},
  ): Promise<ReviewWorkspaceSessionResponse> {
    if (request.force_refresh && !request.replace_existing) {
      throw new ReviewWorkspaceAPIError(
        "force_refresh requires replace_existing.",
        {
          code: "review_request_validation_failed",
          status: 422,
          productionId,
        },
      );
    }

    return this.request(
      productionId,
      "open_session",
      "/session",
      {
        method: "POST",
        body: JSON.stringify({
          force_refresh: request.force_refresh ?? false,
          replace_existing: request.replace_existing ?? false,
        }),
        signal: options.signal,
      },
    );
  }

  getSession(
    productionId: string,
    sessionId?: string | null,
    options: ReviewWorkspaceRequestOptions = {},
  ): Promise<ReviewWorkspaceSessionResponse> {
    return this.request(
      productionId,
      "get_session",
      withSessionQuery("/session", sessionId),
      {
        method: "GET",
        signal: options.signal,
      },
    );
  }

  getSnapshot(
    productionId: string,
    sessionId?: string | null,
    options: ReviewWorkspaceRequestOptions = {},
  ): Promise<ReviewWorkspaceSnapshotResponse> {
    return this.request(
      productionId,
      "get_snapshot",
      withSessionQuery("/snapshot", sessionId),
      {
        method: "GET",
        signal: options.signal,
      },
    );
  }

  resetSession(
    productionId: string,
    request: ResetReviewWorkspaceRequest,
    options: ReviewWorkspaceRequestOptions = {},
  ): Promise<ReviewWorkspaceResetResponse> {
    return this.request(
      productionId,
      "reset_session",
      "/reset",
      {
        method: "POST",
        body: JSON.stringify(normalizeCommandRequest(request, productionId)),
        signal: options.signal,
      },
    );
  }

  closeSession(
    productionId: string,
    request: CloseReviewWorkspaceRequest,
    options: ReviewWorkspaceRequestOptions = {},
  ): Promise<ReviewWorkspaceCloseResponse> {
    return this.request(
      productionId,
      "close_session",
      "/session",
      {
        method: "DELETE",
        body: JSON.stringify(normalizeCommandRequest(request, productionId)),
        signal: options.signal,
      },
    );
  }

  private async request<T>(
    productionId: string,
    expectedOperation: ReviewWorkspaceAPIOperation,
    path: string,
    init: RequestInit,
  ): Promise<T> {
    const normalizedProductionId = requireIdentifier(
      productionId,
      "productionId",
    );

    const url = `${this.baseUrl}/productions/${encodeURIComponent(
      normalizedProductionId,
    )}/review${path}`;

    let response: Response;

    try {
      response = await this.fetcher(url, {
        ...init,
        headers: mergeHeaders(this.headers, init.headers),
      });
    } catch (cause) {
      if (cause instanceof DOMException && cause.name === "AbortError") {
        throw cause;
      }

      throw new ReviewWorkspaceAPIError(
        "Không thể kết nối tới Review Workspace API.",
        {
          code: "network_error",
          status: 0,
          productionId: normalizedProductionId,
          cause,
        },
      );
    }

    const payload = await readJson(response);

    if (!response.ok) {
      throw ReviewWorkspaceAPIError.fromResponse(response, payload);
    }

    validateSuccessResponse(
      payload,
      expectedOperation,
      normalizedProductionId,
    );

    return payload as T;
  }
}

export function createReviewWorkspaceClient(
  config: ReviewWorkspaceClientConfig = {},
): ReviewWorkspaceClient {
  return new ReviewWorkspaceClient(config);
}

function normalizeBaseUrl(value: string): string {
  const normalized = value.trim().replace(/\/+$/, "");

  if (!normalized) {
    throw new Error("Review Workspace API base URL is required.");
  }

  return normalized;
}

function normalizeCommandRequest(
  request: { session_id: string },
  productionId: string,
): { session_id: string } {
  return {
    session_id: requireIdentifier(
      request.session_id,
      "session_id",
      productionId,
    ),
  };
}

function requireIdentifier(
  value: string,
  fieldName: string,
  productionId?: string,
): string {
  const normalized = String(value ?? "").trim();

  if (!normalized) {
    throw new ReviewWorkspaceAPIError(`${fieldName} is required.`, {
      code: "review_request_validation_failed",
      status: 422,
      productionId: productionId ?? null,
    });
  }

  return normalized;
}

function withSessionQuery(
  path: string,
  sessionId?: string | null,
): string {
  if (sessionId === undefined || sessionId === null) {
    return path;
  }

  const normalized = requireIdentifier(sessionId, "session_id");

  return `${path}?session_id=${encodeURIComponent(normalized)}`;
}

function mergeHeaders(
  defaults: HeadersInit,
  requestHeaders?: HeadersInit,
): Headers {
  const headers = new Headers(defaults);

  if (requestHeaders) {
    new Headers(requestHeaders).forEach((value, key) => {
      headers.set(key, value);
    });
  }

  if (!headers.has("Accept")) {
    headers.set("Accept", "application/json");
  }

  if (!headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  return headers;
}

async function readJson(response: Response): Promise<unknown> {
  const text = await response.text();

  if (!text) {
    return null;
  }

  try {
    return JSON.parse(text) as unknown;
  } catch (cause) {
    throw new ReviewWorkspaceAPIError(
      "Review Workspace API returned invalid JSON.",
      {
        code: "invalid_response",
        status: response.status,
        technicalMessage: text.slice(0, 500),
        cause,
      },
    );
  }
}

function validateSuccessResponse(
  payload: unknown,
  expectedOperation: ReviewWorkspaceAPIOperation,
  productionId: string,
): asserts payload is Record<string, unknown> {
  if (!isRecord(payload)) {
    throw invalidResponse(
      "Response payload must be an object.",
      productionId,
    );
  }

  if (
    payload.contract_version !==
    REVIEW_WORKSPACE_API_CONTRACT_VERSION
  ) {
    throw invalidResponse(
      `Unsupported Review Workspace contract version: ${String(
        payload.contract_version,
      )}.`,
      productionId,
    );
  }

  if (payload.success !== true) {
    throw invalidResponse(
      "Successful response must set success=true.",
      productionId,
    );
  }

  if (payload.operation !== expectedOperation) {
    throw invalidResponse(
      `Expected operation ${expectedOperation}, received ${String(
        payload.operation,
      )}.`,
      productionId,
    );
  }

  if (payload.production_id !== productionId) {
    throw invalidResponse(
      "Response production_id does not match the request.",
      productionId,
    );
  }

  if (
    typeof payload.session_id !== "string" ||
    !payload.session_id.trim()
  ) {
    throw invalidResponse(
      "Response session_id is required.",
      productionId,
    );
  }
}

function invalidResponse(
  message: string,
  productionId: string,
): ReviewWorkspaceAPIError {
  return new ReviewWorkspaceAPIError(message, {
    code: "invalid_response",
    status: 502,
    productionId,
  });
}

function isRecord(
  value: unknown,
): value is Record<string, unknown> {
  return (
    typeof value === "object" &&
    value !== null &&
    !Array.isArray(value)
  );
}