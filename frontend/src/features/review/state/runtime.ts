import {
  createStore,
  type StoreApi,
} from "zustand/vanilla";

import {
  ReviewWorkspaceAPIError,
  type ReviewRuntimeSessionSnapshot,
  type ReviewRuntimeSessionState,
} from "../api";

import type {
  ReviewWorkspaceRuntimeActionOptions,
  ReviewWorkspaceRuntimeClient,
  ReviewWorkspaceRuntimeError,
  ReviewWorkspaceRuntimeListener,
  ReviewWorkspaceRuntimeOpenOptions,
  ReviewWorkspaceRuntimeState,
} from "./contracts";

const INITIAL_STATE: ReviewWorkspaceRuntimeState = {
  status: "idle",
  pendingOperation: null,
  productionId: null,
  sessionId: null,
  session: null,
  snapshot: null,
  error: null,
  requestRevision: 0,
  stateRevision: 0,
  updatedAt: null,
};

export class ReviewWorkspaceSessionRuntime {
  private readonly store: StoreApi<ReviewWorkspaceRuntimeState>;
  private activeController: AbortController | null = null;
  private disposed = false;

  constructor(
    private readonly client: ReviewWorkspaceRuntimeClient,
  ) {
    this.store = createStore<ReviewWorkspaceRuntimeState>(
      () => clone(INITIAL_STATE),
    );
  }

  getState(): ReviewWorkspaceRuntimeState {
    return clone(this.store.getState());
  }

  subscribe(
    listener: ReviewWorkspaceRuntimeListener,
  ): () => void {
    this.assertNotDisposed();

    return this.store.subscribe(
      (state, previousState) => {
        listener(
          clone(state),
          clone(previousState),
        );
      },
    );
  }

  async open(
    productionId: string,
    options: ReviewWorkspaceRuntimeOpenOptions = {},
  ): Promise<ReviewWorkspaceRuntimeState> {
    this.assertNotDisposed();

    const normalizedProductionId = requireIdentifier(
      productionId,
      "productionId",
    );

    const request = this.beginRequest(
      "opening",
      "open",
      {
        productionId: normalizedProductionId,
        sessionId: null,
        session: null,
        snapshot: null,
      },
    );

    const signal = linkAbortSignals(
      request.controller,
      options.signal,
    );

    try {
      const response = await this.client.openSession(
        normalizedProductionId,
        {
          force_refresh: options.force_refresh,
          replace_existing: options.replace_existing,
        },
        { signal },
      );

      this.completeRequest(request.revision, {
        status: "ready",
        productionId: response.production_id,
        sessionId: response.session_id,
        session: response.session,
        snapshot: response.snapshot,
      });

      return this.getState();
    } catch (error) {
      this.failRequest(request.revision, error);
      throw error;
    }
  }

  async refresh(
    options: ReviewWorkspaceRuntimeActionOptions = {},
  ): Promise<ReviewWorkspaceRuntimeState> {
    const active = this.requireActiveSession();

    const request = this.beginRequest(
      "refreshing",
      "refresh",
    );

    const signal = linkAbortSignals(
      request.controller,
      options.signal,
    );

    try {
      const response = await this.client.getSnapshot(
        active.productionId,
        active.sessionId,
        { signal },
      );

      this.completeRequest(request.revision, {
        status: "ready",
        productionId: response.production_id,
        sessionId: response.session_id,
        session: response.snapshot.session,
        snapshot: response.snapshot,
      });

      return this.getState();
    } catch (error) {
      this.failRequest(request.revision, error);
      throw error;
    }
  }

  async reset(
    options: ReviewWorkspaceRuntimeActionOptions = {},
  ): Promise<ReviewWorkspaceRuntimeState> {
    const active = this.requireActiveSession();

    const request = this.beginRequest(
      "resetting",
      "reset",
    );

    const signal = linkAbortSignals(
      request.controller,
      options.signal,
    );

    try {
      const response = await this.client.resetSession(
        active.productionId,
        {
          session_id: active.sessionId,
        },
        { signal },
      );

      this.completeRequest(request.revision, {
        status: "ready",
        productionId: response.production_id,
        sessionId: response.session_id,
        session: response.snapshot.session,
        snapshot: response.snapshot,
      });

      return this.getState();
    } catch (error) {
      this.failRequest(request.revision, error);
      throw error;
    }
  }

  async close(
    options: ReviewWorkspaceRuntimeActionOptions = {},
  ): Promise<ReviewWorkspaceRuntimeState> {
    const active = this.requireActiveSession();

    const request = this.beginRequest(
      "closing",
      "close",
    );

    const signal = linkAbortSignals(
      request.controller,
      options.signal,
    );

    try {
      const response = await this.client.closeSession(
        active.productionId,
        {
          session_id: active.sessionId,
        },
        { signal },
      );

      this.completeRequest(request.revision, {
        status: "closed",
        productionId: response.production_id,
        sessionId: response.session_id,
        session: response.state,
        snapshot: null,
      });

      return this.getState();
    } catch (error) {
      this.failRequest(request.revision, error);
      throw error;
    }
  }

  clear(): ReviewWorkspaceRuntimeState {
    this.assertNotDisposed();
    this.cancelActiveRequest();

    const current = this.store.getState();

    this.store.setState({
      ...clone(INITIAL_STATE),
      requestRevision:
        current.requestRevision + 1,
      stateRevision:
        current.stateRevision + 1,
      updatedAt: now(),
    });

    return this.getState();
  }

  dispose(): void {
    if (this.disposed) {
      return;
    }

    this.cancelActiveRequest();
    this.disposed = true;
  }

  private beginRequest(
    status: ReviewWorkspaceRuntimeState["status"],
    pendingOperation: Exclude<
      ReviewWorkspaceRuntimeState["pendingOperation"],
      null
    >,
    replacement:
      Partial<ReviewWorkspaceRuntimeState> = {},
  ): {
    revision: number;
    controller: AbortController;
  } {
    this.assertNotDisposed();
    this.cancelActiveRequest();

    const current = this.store.getState();
    const revision =
      current.requestRevision + 1;
    const controller =
      new AbortController();

    this.activeController = controller;

    this.store.setState({
      ...current,
      ...clone(replacement),
      status,
      pendingOperation,
      error: null,
      requestRevision: revision,
      stateRevision:
        current.stateRevision + 1,
      updatedAt: now(),
    });

    return {
      revision,
      controller,
    };
  }

  private completeRequest(
    revision: number,
    replacement: {
      status: "ready" | "closed";
      productionId: string;
      sessionId: string;
      session: ReviewRuntimeSessionState;
      snapshot:
        ReviewRuntimeSessionSnapshot | null;
    },
  ): void {
    const current = this.store.getState();

    if (
      revision !== current.requestRevision ||
      this.disposed
    ) {
      return;
    }

    this.activeController = null;

    this.store.setState({
      ...current,
      ...clone(replacement),
      pendingOperation: null,
      error: null,
      stateRevision:
        current.stateRevision + 1,
      updatedAt: now(),
    });
  }

  private failRequest(
    revision: number,
    error: unknown,
  ): void {
    const current = this.store.getState();

    if (
      revision !== current.requestRevision ||
      this.disposed
    ) {
      return;
    }

    this.activeController = null;

    this.store.setState({
      ...current,
      status: "error",
      pendingOperation: null,
      error: normalizeError(error),
      stateRevision:
        current.stateRevision + 1,
      updatedAt: now(),
    });
  }

  private requireActiveSession(): {
    productionId: string;
    sessionId: string;
  } {
    this.assertNotDisposed();

    const state = this.store.getState();

    if (
      !state.productionId ||
      !state.sessionId ||
      !state.session
    ) {
      throw new ReviewWorkspaceAPIError(
        "Review Workspace session is not open.",
        {
          code: "review_session_not_found",
          status: 409,
          productionId: state.productionId,
          sessionId: state.sessionId,
        },
      );
    }

    if (state.status === "closed") {
      throw new ReviewWorkspaceAPIError(
        "Review Workspace session is closed.",
        {
          code: "review_session_not_found",
          status: 409,
          productionId: state.productionId,
          sessionId: state.sessionId,
        },
      );
    }

    return {
      productionId: state.productionId,
      sessionId: state.sessionId,
    };
  }

  private cancelActiveRequest(): void {
    this.activeController?.abort();
    this.activeController = null;
  }

  private assertNotDisposed(): void {
    if (this.disposed) {
      throw new Error(
        "ReviewWorkspaceSessionRuntime has been disposed.",
      );
    }
  }
}

function normalizeError(
  error: unknown,
): ReviewWorkspaceRuntimeError {
  if (error instanceof ReviewWorkspaceAPIError) {
    return {
      name: error.name,
      message: error.message,
      code: error.code,
      status: error.status,
      technicalMessage:
        error.technicalMessage,
      productionId: error.productionId,
      sessionId: error.sessionId,
    };
  }

  return {
    name:
      error instanceof Error
        ? error.name
        : "Error",
    message:
      error instanceof Error
        ? error.message
        : String(error),
    code: "unknown_error",
    status: null,
    technicalMessage: null,
    productionId: null,
    sessionId: null,
  };
}

function requireIdentifier(
  value: string,
  fieldName: string,
): string {
  const normalized =
    String(value ?? "").trim();

  if (!normalized) {
    throw new Error(
      `${fieldName} is required.`,
    );
  }

  return normalized;
}

function linkAbortSignals(
  controller: AbortController,
  externalSignal?: AbortSignal,
): AbortSignal {
  if (!externalSignal) {
    return controller.signal;
  }

  if (externalSignal.aborted) {
    controller.abort(
      externalSignal.reason,
    );

    return controller.signal;
  }

  externalSignal.addEventListener(
    "abort",
    () => {
      controller.abort(
        externalSignal.reason,
      );
    },
    { once: true },
  );

  return controller.signal;
}

function clone<T>(value: T): T {
  return structuredClone(value);
}

function now(): string {
  return new Date().toISOString();
}