import type {
  JsonObject,
  ReviewWorkspaceAPIErrorCode,
  ReviewWorkspaceErrorResponse,
} from "./contracts";

export interface ReviewWorkspaceAPIErrorOptions {
  code: ReviewWorkspaceAPIErrorCode;
  status: number;
  technicalMessage?: string | null;
  productionId?: string | null;
  sessionId?: string | null;
  metadata?: JsonObject;
  cause?: unknown;
}

export class ReviewWorkspaceAPIError extends Error {
  readonly code: ReviewWorkspaceAPIErrorCode;
  readonly status: number;
  readonly technicalMessage: string | null;
  readonly productionId: string | null;
  readonly sessionId: string | null;
  readonly metadata: JsonObject;

  constructor(
    message: string,
    options: ReviewWorkspaceAPIErrorOptions,
  ) {
    super(message, { cause: options.cause });

    this.name = "ReviewWorkspaceAPIError";
    this.code = options.code;
    this.status = options.status;
    this.technicalMessage =
      options.technicalMessage ?? null;
    this.productionId =
      options.productionId ?? null;
    this.sessionId =
      options.sessionId ?? null;
    this.metadata = options.metadata ?? {};
  }

  get isRevisionConflict(): boolean {
    return (
      this.status === 409 &&
      this.code === "review_session_conflict" &&
      this.expectedRevision !== null &&
      this.currentRevision !== null
    );
  }

  get expectedRevision(): number | null {
    return readApplicationErrorNumber(
      this.metadata,
      "expected_revision",
    );
  }

  get currentRevision(): number | null {
    return readApplicationErrorNumber(
      this.metadata,
      "current_revision",
    );
  }

  static fromResponse(
    response: Response,
    payload: unknown,
  ): ReviewWorkspaceAPIError {
    if (isReviewWorkspaceErrorResponse(payload)) {
      return new ReviewWorkspaceAPIError(
        payload.error.message,
        {
          code: payload.error.code,
          status: response.status,
          technicalMessage:
            payload.error.technical_message,
          productionId:
            payload.error.production_id,
          sessionId:
            payload.error.session_id,
          metadata: payload.error.metadata,
        },
      );
    }

    return new ReviewWorkspaceAPIError(
      extractFastAPIMessage(payload) ??
        `HTTP request failed with status ${response.status}.`,
      {
        code: "http_error",
        status: response.status,
        technicalMessage:
          response.statusText || null,
      },
    );
  }
}

export function isReviewWorkspaceErrorResponse(
  value: unknown,
): value is ReviewWorkspaceErrorResponse {
  if (
    !isRecord(value) ||
    value.success !== false ||
    !isRecord(value.error)
  ) {
    return false;
  }

  return (
    typeof value.contract_version === "string" &&
    typeof value.error.code === "string" &&
    typeof value.error.message === "string"
  );
}

function readApplicationErrorNumber(
  metadata: JsonObject,
  key: string,
): number | null {
  const applicationError =
    metadata.application_error;

  if (!isRecord(applicationError)) {
    return null;
  }

  const value = applicationError[key];

  return (
    typeof value === "number" &&
    Number.isInteger(value)
  )
    ? value
    : null;
}

function extractFastAPIMessage(
  payload: unknown,
): string | null {
  if (!isRecord(payload)) {
    return null;
  }

  if (typeof payload.detail === "string") {
    return payload.detail;
  }

  if (Array.isArray(payload.detail)) {
    const messages = payload.detail
      .map((item) =>
        isRecord(item) &&
        typeof item.msg === "string"
          ? item.msg
          : null,
      )
      .filter(
        (message): message is string =>
          message !== null,
      );

    return messages.length > 0
      ? messages.join("; ")
      : null;
  }

  return null;
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