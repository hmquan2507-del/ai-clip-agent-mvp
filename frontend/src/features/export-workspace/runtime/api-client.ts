import type {
  ExportRenderContract,
  ExportRenderStatusResponse,
  ExportSubmissionResponse,
} from "./types";

export type FetchLike = typeof fetch;

export class ExportWorkspaceApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly payload: unknown,
  ) {
    super(message);
    this.name = "ExportWorkspaceApiError";
  }
}

function trimTrailingSlash(value: string): string {
  return value.replace(/\/+$/, "");
}

async function parseJson(response: Response): Promise<unknown> {
  const text = await response.text();

  if (!text) {
    return null;
  }

  try {
    return JSON.parse(text) as unknown;
  } catch {
    return { detail: text };
  }
}

export class ExportWorkspaceApiClient {
  private readonly baseUrl: string;
  private readonly fetchImpl: FetchLike;

  constructor(options?: {
    baseUrl?: string;
    fetchImpl?: FetchLike;
  }) {
    this.baseUrl = trimTrailingSlash(
      options?.baseUrl ??
        process.env.NEXT_PUBLIC_API_URL ??
        "http://localhost:8000",
    );
    this.fetchImpl = options?.fetchImpl ?? fetch;
  }

  async submitRender(
    contract: ExportRenderContract,
    signal?: AbortSignal,
  ): Promise<ExportSubmissionResponse> {
    const response = await this.fetchImpl(
      `${this.baseUrl}/api/v1/export-workspace/render-submissions`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(contract),
        signal,
      },
    );

    const payload = await parseJson(response);

    if (!response.ok) {
      throw new ExportWorkspaceApiError(
        `Render submission failed with HTTP ${response.status}.`,
        response.status,
        payload,
      );
    }

    return payload as ExportSubmissionResponse;
  }

  async getRenderStatus(
    queueJobId: string,
    signal?: AbortSignal,
  ): Promise<ExportRenderStatusResponse> {
    const response = await this.fetchImpl(
      `${this.baseUrl}/api/v1/export-workspace/render-submissions/${encodeURIComponent(queueJobId)}`,
      {
        method: "GET",
        headers: {
          Accept: "application/json",
        },
        signal,
      },
    );

    const payload = await parseJson(response);

    if (!response.ok) {
      throw new ExportWorkspaceApiError(
        `Render status request failed with HTTP ${response.status}.`,
        response.status,
        payload,
      );
    }

    return payload as ExportRenderStatusResponse;
  }
}
