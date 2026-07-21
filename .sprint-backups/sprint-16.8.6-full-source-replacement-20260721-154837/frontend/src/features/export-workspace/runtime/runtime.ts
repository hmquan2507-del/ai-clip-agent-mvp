import { ExportWorkspaceApiClient } from "./api-client";
import {
  initialExportRuntimeState,
  type ExportRenderContract,
  type ExportRenderStatusData,
  type ExportRuntimeState,
} from "./types";

type Listener = () => void;

export type ExportRuntimeOptions = {
  pollIntervalMs?: number;
  terminalStatuses?: readonly string[];
};

export class ExportWorkspaceRuntime {
  private state: ExportRuntimeState = initialExportRuntimeState;
  private readonly listeners = new Set<Listener>();
  private readonly pollIntervalMs: number;
  private readonly terminalStatuses: Set<string>;
  private abortController: AbortController | null = null;
  private pollTimer: ReturnType<typeof setTimeout> | null = null;

  constructor(
    private readonly apiClient: ExportWorkspaceApiClient,
    options?: ExportRuntimeOptions,
  ) {
    this.pollIntervalMs = Math.max(options?.pollIntervalMs ?? 1500, 100);
    this.terminalStatuses = new Set(
      (options?.terminalStatuses ?? ["completed", "failed", "cancelled"]).map(
        (status) => status.toLowerCase(),
      ),
    );
  }

  subscribe = (listener: Listener): (() => void) => {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  };

  getSnapshot = (): ExportRuntimeState => this.state;

  reset(): void {
    this.stopActiveRequest();
    this.setState(initialExportRuntimeState);
  }

  cancel(): void {
    this.stopActiveRequest();
    this.setState({
      ...this.state,
      phase: "cancelled",
      error: null,
    });
  }

  async submit(contract: ExportRenderContract): Promise<void> {
    this.stopActiveRequest();
    this.abortController = new AbortController();

    this.setState({
      phase: "submitting",
      submission: null,
      status: null,
      error: null,
    });

    try {
      const response = await this.apiClient.submitRender(
        contract,
        this.abortController.signal,
      );

      if (!response.success || !response.data) {
        this.setState({
          phase: "failed",
          submission: null,
          status: null,
          error:
            response.error ??
            response.error_code ??
            "Render submission was rejected.",
        });
        return;
      }

      this.setState({
        phase: "queued",
        submission: response.data,
        status: null,
        error: null,
      });

      await this.poll(response.data.queue_job_id);
    } catch (error) {
      if (this.abortController?.signal.aborted) {
        return;
      }

      this.fail(error);
    }
  }

  private async poll(queueJobId: string): Promise<void> {
    if (!this.abortController) {
      return;
    }

    this.setState({
      ...this.state,
      phase: "polling",
    });

    try {
      const response = await this.apiClient.getRenderStatus(
        queueJobId,
        this.abortController.signal,
      );

      const status = response.data;
      const normalizedStatus = status.status.toLowerCase();

      if (this.terminalStatuses.has(normalizedStatus)) {
        this.setTerminalState(status, normalizedStatus);
        return;
      }

      this.setState({
        ...this.state,
        phase: "polling",
        status,
        error: null,
      });

      this.pollTimer = setTimeout(() => {
        void this.poll(queueJobId);
      }, this.pollIntervalMs);
    } catch (error) {
      if (this.abortController.signal.aborted) {
        return;
      }

      this.fail(error);
    }
  }

  private setTerminalState(
    status: ExportRenderStatusData,
    normalizedStatus: string,
  ): void {
    const phase =
      normalizedStatus === "completed"
        ? "completed"
        : normalizedStatus === "cancelled"
          ? "cancelled"
          : "failed";

    this.setState({
      ...this.state,
      phase,
      status,
      error: phase === "failed" ? status.error ?? "Render failed." : null,
    });

    this.stopActiveRequest();
  }

  private fail(error: unknown): void {
    const message =
      error instanceof Error ? error.message : "Unknown Export Workspace error.";

    this.setState({
      ...this.state,
      phase: "failed",
      error: message,
    });

    this.stopActiveRequest();
  }

  private stopActiveRequest(): void {
    if (this.pollTimer) {
      clearTimeout(this.pollTimer);
      this.pollTimer = null;
    }

    if (this.abortController) {
      this.abortController.abort();
      this.abortController = null;
    }
  }

  private setState(nextState: ExportRuntimeState): void {
    this.state = nextState;
    this.listeners.forEach((listener) => listener());
  }
}
