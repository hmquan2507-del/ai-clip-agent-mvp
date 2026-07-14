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
import {
  REVIEW_TIMELINE_COMMAND_API_CONTRACT_VERSION,
  type CloseTimelineGapRequest,
  type DeleteTimelineClipRequest,
  type DuplicateTimelineClipRequest,
  type MoveTimelineClipRequest,
  type RedoTimelineCommandRequest,
  type ReviewTimelineCommandOperation,
  type ReviewTimelineCommandRequest,
  type ReviewTimelineCommandResponse,
  type SplitTimelineClipRequest,
  type TrimTimelineClipEndRequest,
  type TrimTimelineClipStartRequest,
  type UndoTimelineCommandRequest,
} from "./timeline-contracts";

const DEFAULT_API_BASE_URL =
  "http://localhost:8000/api/v1";

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

  constructor(
    config: ReviewWorkspaceClientConfig = {},
  ) {
    this.baseUrl = normalizeBaseUrl(
      config.baseUrl ??
        process.env.NEXT_PUBLIC_API_BASE_URL ??
        DEFAULT_API_BASE_URL,
    );

    this.fetcher =
      config.fetch ??
      globalThis.fetch.bind(globalThis);

    this.headers = config.headers ?? {};
  }

  openSession(
    productionId: string,
    request: OpenReviewWorkspaceRequest = {},
    options: ReviewWorkspaceRequestOptions = {},
  ): Promise<ReviewWorkspaceSessionResponse> {
    if (
      request.force_refresh &&
      !request.replace_existing
    ) {
      throw new ReviewWorkspaceAPIError(
        "force_refresh requires replace_existing.",
        {
          code:
            "review_request_validation_failed",
          status: 422,
          productionId,
        },
      );
    }

    return this.requestWorkspace(
      productionId,
      "open_session",
      "/session",
      {
        method: "POST",
        body: JSON.stringify({
          force_refresh:
            request.force_refresh ?? false,
          replace_existing:
            request.replace_existing ?? false,
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
    return this.requestWorkspace(
      productionId,
      "get_session",
      withSessionQuery(
        "/session",
        sessionId,
      ),
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
    return this.requestWorkspace(
      productionId,
      "get_snapshot",
      withSessionQuery(
        "/snapshot",
        sessionId,
      ),
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
    return this.requestWorkspace(
      productionId,
      "reset_session",
      "/reset",
      {
        method: "POST",
        body: JSON.stringify(
          normalizeSessionCommand(
            request,
            productionId,
          ),
        ),
        signal: options.signal,
      },
    );
  }

  closeSession(
    productionId: string,
    request: CloseReviewWorkspaceRequest,
    options: ReviewWorkspaceRequestOptions = {},
  ): Promise<ReviewWorkspaceCloseResponse> {
    return this.requestWorkspace(
      productionId,
      "close_session",
      "/session",
      {
        method: "DELETE",
        body: JSON.stringify(
          normalizeSessionCommand(
            request,
            productionId,
          ),
        ),
        signal: options.signal,
      },
    );
  }

  moveClip(
    productionId: string,
    request: MoveTimelineClipRequest,
    options: ReviewWorkspaceRequestOptions = {},
  ): Promise<ReviewTimelineCommandResponse> {
    return this.requestTimeline(
      productionId,
      "move_clip",
      "/timeline/move",
      {
        ...normalizeTimelineCommand(
          request,
          productionId,
        ),
        clip_id: requireIdentifier(
          request.clip_id,
          "clip_id",
          productionId,
        ),
        new_start_time:
          requireNonNegativeNumber(
            request.new_start_time,
            "new_start_time",
            productionId,
          ),
        target_track_id:
          normalizeOptionalIdentifier(
            request.target_track_id,
            "target_track_id",
            productionId,
          ),
      },
      options,
    );
  }

  trimClipStart(
    productionId: string,
    request: TrimTimelineClipStartRequest,
    options: ReviewWorkspaceRequestOptions = {},
  ): Promise<ReviewTimelineCommandResponse> {
    return this.requestTimeline(
      productionId,
      "trim_clip_start",
      "/timeline/trim-start",
      {
        ...normalizeTimelineCommand(
          request,
          productionId,
        ),
        clip_id: requireIdentifier(
          request.clip_id,
          "clip_id",
          productionId,
        ),
        new_start_time:
          requireNonNegativeNumber(
            request.new_start_time,
            "new_start_time",
            productionId,
          ),
      },
      options,
    );
  }

  trimClipEnd(
    productionId: string,
    request: TrimTimelineClipEndRequest,
    options: ReviewWorkspaceRequestOptions = {},
  ): Promise<ReviewTimelineCommandResponse> {
    return this.requestTimeline(
      productionId,
      "trim_clip_end",
      "/timeline/trim-end",
      {
        ...normalizeTimelineCommand(
          request,
          productionId,
        ),
        clip_id: requireIdentifier(
          request.clip_id,
          "clip_id",
          productionId,
        ),
        new_end_time:
          requirePositiveNumber(
            request.new_end_time,
            "new_end_time",
            productionId,
          ),
      },
      options,
    );
  }

  splitClip(
    productionId: string,
    request: SplitTimelineClipRequest,
    options: ReviewWorkspaceRequestOptions = {},
  ): Promise<ReviewTimelineCommandResponse> {
    return this.requestTimeline(
      productionId,
      "split_clip",
      "/timeline/split",
      {
        ...normalizeTimelineCommand(
          request,
          productionId,
        ),
        clip_id: requireIdentifier(
          request.clip_id,
          "clip_id",
          productionId,
        ),
        split_time:
          requirePositiveNumber(
            request.split_time,
            "split_time",
            productionId,
          ),
        right_clip_id:
          normalizeOptionalIdentifier(
            request.right_clip_id,
            "right_clip_id",
            productionId,
          ),
      },
      options,
    );
  }

  duplicateClip(
    productionId: string,
    request: DuplicateTimelineClipRequest,
    options: ReviewWorkspaceRequestOptions = {},
  ): Promise<ReviewTimelineCommandResponse> {
    const newStartTime =
      request.new_start_time === undefined ||
      request.new_start_time === null
        ? undefined
        : requireNonNegativeNumber(
            request.new_start_time,
            "new_start_time",
            productionId,
          );

    return this.requestTimeline(
      productionId,
      "duplicate_clip",
      "/timeline/duplicate",
      {
        ...normalizeTimelineCommand(
          request,
          productionId,
        ),
        clip_id: requireIdentifier(
          request.clip_id,
          "clip_id",
          productionId,
        ),
        new_clip_id:
          normalizeOptionalIdentifier(
            request.new_clip_id,
            "new_clip_id",
            productionId,
          ),
        new_start_time: newStartTime,
        target_track_id:
          normalizeOptionalIdentifier(
            request.target_track_id,
            "target_track_id",
            productionId,
          ),
      },
      options,
    );
  }

  deleteClip(
    productionId: string,
    request: DeleteTimelineClipRequest,
    options: ReviewWorkspaceRequestOptions = {},
  ): Promise<ReviewTimelineCommandResponse> {
    return this.requestTimeline(
      productionId,
      "delete_clip",
      "/timeline/delete",
      {
        ...normalizeTimelineCommand(
          request,
          productionId,
        ),
        clip_id: requireIdentifier(
          request.clip_id,
          "clip_id",
          productionId,
        ),
        close_gap:
          request.close_gap ?? false,
      },
      options,
    );
  }

  closeGap(
    productionId: string,
    request: CloseTimelineGapRequest,
    options: ReviewWorkspaceRequestOptions = {},
  ): Promise<ReviewTimelineCommandResponse> {
    const gapStart =
      requireNonNegativeNumber(
        request.gap_start,
        "gap_start",
        productionId,
      );

    const gapEnd =
      requirePositiveNumber(
        request.gap_end,
        "gap_end",
        productionId,
      );

    if (gapEnd <= gapStart) {
      throw validationError(
        "gap_end must be greater than gap_start.",
        productionId,
      );
    }

    return this.requestTimeline(
      productionId,
      "close_gap",
      "/timeline/close-gap",
      {
        ...normalizeTimelineCommand(
          request,
          productionId,
        ),
        track_id: requireIdentifier(
          request.track_id,
          "track_id",
          productionId,
        ),
        gap_start: gapStart,
        gap_end: gapEnd,
      },
      options,
    );
  }

  undoTimeline(
    productionId: string,
    request: UndoTimelineCommandRequest,
    options: ReviewWorkspaceRequestOptions = {},
  ): Promise<ReviewTimelineCommandResponse> {
    return this.requestTimeline(
      productionId,
      "undo",
      "/timeline/undo",
      normalizeTimelineCommand(
        request,
        productionId,
      ),
      options,
    );
  }

  redoTimeline(
    productionId: string,
    request: RedoTimelineCommandRequest,
    options: ReviewWorkspaceRequestOptions = {},
  ): Promise<ReviewTimelineCommandResponse> {
    return this.requestTimeline(
      productionId,
      "redo",
      "/timeline/redo",
      normalizeTimelineCommand(
        request,
        productionId,
      ),
      options,
    );
  }

  private async requestWorkspace<T>(
    productionId: string,
    expectedOperation:
      ReviewWorkspaceAPIOperation,
    path: string,
    init: RequestInit,
  ): Promise<T> {
    const normalizedProductionId =
      requireIdentifier(
        productionId,
        "productionId",
      );

    const payload = await this.send(
      normalizedProductionId,
      path,
      init,
    );

    validateWorkspaceSuccessResponse(
      payload,
      expectedOperation,
      normalizedProductionId,
    );

    return payload as T;
  }

  private async requestTimeline(
    productionId: string,
    expectedOperation:
      ReviewTimelineCommandOperation,
    path: string,
    body: Record<string, unknown>,
    options: ReviewWorkspaceRequestOptions,
  ): Promise<ReviewTimelineCommandResponse> {
    const normalizedProductionId =
      requireIdentifier(
        productionId,
        "productionId",
      );

    const payload = await this.send(
      normalizedProductionId,
      path,
      {
        method: "POST",
        body: JSON.stringify(
          removeUndefined(body),
        ),
        signal: options.signal,
      },
    );

    validateTimelineSuccessResponse(
      payload,
      expectedOperation,
      normalizedProductionId,
    );

    return payload;
  }

  private async send(
    productionId: string,
    path: string,
    init: RequestInit,
  ): Promise<unknown> {
    const url =
      `${this.baseUrl}/productions/` +
      `${encodeURIComponent(productionId)}` +
      `/review${path}`;

    let response: Response;

    try {
      response = await this.fetcher(
        url,
        {
          ...init,
          headers: mergeHeaders(
            this.headers,
            init.headers,
          ),
        },
      );
    } catch (cause) {
      if (
        cause instanceof DOMException &&
        cause.name === "AbortError"
      ) {
        throw cause;
      }

      throw new ReviewWorkspaceAPIError(
        "Không thể kết nối tới Review Workspace API.",
        {
          code: "network_error",
          status: 0,
          productionId,
          cause,
        },
      );
    }

    const payload = await readJson(
      response,
    );

    if (!response.ok) {
      throw (
        ReviewWorkspaceAPIError
        .fromResponse(
          response,
          payload,
        )
      );
    }

    return payload;
  }
}

export function createReviewWorkspaceClient(
  config: ReviewWorkspaceClientConfig = {},
): ReviewWorkspaceClient {
  return new ReviewWorkspaceClient(
    config,
  );
}

function normalizeBaseUrl(
  value: string,
): string {
  const normalized =
    value.trim().replace(/\/+$/, "");

  if (!normalized) {
    throw new Error(
      "Review Workspace API base URL is required.",
    );
  }

  return normalized;
}

function normalizeSessionCommand(
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

function normalizeTimelineCommand(
  request: ReviewTimelineCommandRequest,
  productionId: string,
): {
  session_id: string;
  expected_revision?: number;
} {
  const normalized: {
    session_id: string;
    expected_revision?: number;
  } = {
    session_id: requireIdentifier(
      request.session_id,
      "session_id",
      productionId,
    ),
  };

  if (
    request.expected_revision !== undefined &&
    request.expected_revision !== null
  ) {
    normalized.expected_revision =
      requirePositiveInteger(
        request.expected_revision,
        "expected_revision",
        productionId,
      );
  }

  return normalized;
}

function normalizeOptionalIdentifier(
  value: string | null | undefined,
  fieldName: string,
  productionId: string,
): string | undefined {
  if (
    value === undefined ||
    value === null
  ) {
    return undefined;
  }

  return requireIdentifier(
    value,
    fieldName,
    productionId,
  );
}

function requireIdentifier(
  value: string,
  fieldName: string,
  productionId?: string,
): string {
  const normalized =
    String(value ?? "").trim();

  if (!normalized) {
    throw validationError(
      `${fieldName} is required.`,
      productionId,
    );
  }

  return normalized;
}

function requireNonNegativeNumber(
  value: number,
  fieldName: string,
  productionId: string,
): number {
  if (
    typeof value !== "number" ||
    !Number.isFinite(value) ||
    value < 0
  ) {
    throw validationError(
      `${fieldName} must be a finite number greater than or equal to 0.`,
      productionId,
    );
  }

  return value;
}

function requirePositiveNumber(
  value: number,
  fieldName: string,
  productionId: string,
): number {
  if (
    typeof value !== "number" ||
    !Number.isFinite(value) ||
    value <= 0
  ) {
    throw validationError(
      `${fieldName} must be a finite number greater than 0.`,
      productionId,
    );
  }

  return value;
}

function requirePositiveInteger(
  value: number,
  fieldName: string,
  productionId: string,
): number {
  if (
    !Number.isInteger(value) ||
    value < 1
  ) {
    throw validationError(
      `${fieldName} must be an integer greater than or equal to 1.`,
      productionId,
    );
  }

  return value;
}

function validationError(
  message: string,
  productionId?: string,
): ReviewWorkspaceAPIError {
  return new ReviewWorkspaceAPIError(
    message,
    {
      code:
        "review_request_validation_failed",
      status: 422,
      productionId:
        productionId ?? null,
    },
  );
}

function withSessionQuery(
  path: string,
  sessionId?: string | null,
): string {
  if (
    sessionId === undefined ||
    sessionId === null
  ) {
    return path;
  }

  const normalized =
    requireIdentifier(
      sessionId,
      "session_id",
    );

  return (
    `${path}?session_id=` +
    `${encodeURIComponent(normalized)}`
  );
}

function mergeHeaders(
  defaults: HeadersInit,
  requestHeaders?: HeadersInit,
): Headers {
  const headers =
    new Headers(defaults);

  if (requestHeaders) {
    new Headers(
      requestHeaders,
    ).forEach(
      (value, key) => {
        headers.set(key, value);
      },
    );
  }

  if (!headers.has("Accept")) {
    headers.set(
      "Accept",
      "application/json",
    );
  }

  if (!headers.has("Content-Type")) {
    headers.set(
      "Content-Type",
      "application/json",
    );
  }

  return headers;
}

async function readJson(
  response: Response,
): Promise<unknown> {
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
        technicalMessage:
          text.slice(0, 500),
        cause,
      },
    );
  }
}

function validateWorkspaceSuccessResponse(
  payload: unknown,
  expectedOperation:
    ReviewWorkspaceAPIOperation,
  productionId: string,
): asserts payload is Record<string, unknown> {
  validateCommonSuccessResponse(
    payload,
    REVIEW_WORKSPACE_API_CONTRACT_VERSION,
    expectedOperation,
    productionId,
  );
}

function validateTimelineSuccessResponse(
  payload: unknown,
  expectedOperation:
    ReviewTimelineCommandOperation,
  productionId: string,
): asserts payload is ReviewTimelineCommandResponse {
  validateCommonSuccessResponse(
    payload,
    REVIEW_TIMELINE_COMMAND_API_CONTRACT_VERSION,
    expectedOperation,
    productionId,
  );

  if (
    !isRecord(payload.snapshot) ||
    !isRecord(payload.history) ||
    (
      payload.command !== null &&
      !isRecord(payload.command)
    ) ||
    (
      payload.event !== null &&
      !isRecord(payload.event)
    ) ||
    !isRecord(payload.metadata)
  ) {
    throw invalidResponse(
      "Timeline command response payload is incomplete.",
      productionId,
    );
  }
}

function validateCommonSuccessResponse(
  payload: unknown,
  expectedContractVersion: string,
  expectedOperation: string,
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
    expectedContractVersion
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

  if (
    payload.operation !==
    expectedOperation
  ) {
    throw invalidResponse(
      `Expected operation ${expectedOperation}, received ${String(
        payload.operation,
      )}.`,
      productionId,
    );
  }

  if (
    payload.production_id !==
    productionId
  ) {
    throw invalidResponse(
      "Response production_id does not match the request.",
      productionId,
    );
  }

  if (
    typeof payload.session_id !==
      "string" ||
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
  return new ReviewWorkspaceAPIError(
    message,
    {
      code: "invalid_response",
      status: 502,
      productionId,
    },
  );
}

function removeUndefined(
  value: Record<string, unknown>,
): Record<string, unknown> {
  return Object.fromEntries(
    Object.entries(value).filter(
      ([, item]) =>
        item !== undefined,
    ),
  );
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