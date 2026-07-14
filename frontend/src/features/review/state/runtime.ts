import {
  createStore,
  type StoreApi,
} from "zustand/vanilla";

import {
  ReviewWorkspaceAPIError,
  type ReviewRuntimeSessionSnapshot,
  type ReviewRuntimeSessionState,
  type ReviewTimelineCommandOperation,
  type ReviewTimelineCommandResponse,
} from "../api";

import type {
  CloseTimelineGapInput,
  DeleteTimelineClipInput,
  DuplicateTimelineClipInput,
  MoveTimelineClipInput,
  ReviewWorkspaceRuntimeActionOptions,
  ReviewWorkspaceRuntimeClient,
  ReviewWorkspaceRuntimeError,
  ReviewWorkspaceRuntimeListener,
  ReviewWorkspaceRuntimeOpenOptions,
  ReviewWorkspaceRuntimeState,
  SplitTimelineClipInput,
  TrimTimelineClipEndInput,
  TrimTimelineClipStartInput,
} from "./contracts";

const INITIAL_STATE: ReviewWorkspaceRuntimeState = {
  status: "idle",
  pendingOperation: null,
  pendingCommand: null,
  lastCommand: null,
  lastCommandResponse: null,
  productionId: null,
  sessionId: null,
  session: null,
  snapshot: null,
  error: null,
  requestRevision: 0,
  stateRevision: 0,
  updatedAt: null,
};

interface ActiveSession {
  productionId: string;
  sessionId: string;
  snapshot: ReviewRuntimeSessionSnapshot;
}

interface RuntimeRequest {
  revision: number;
  controller: AbortController;
}

type TimelineCommandExecutor = (
  active: ActiveSession,
  expectedRevision: number,
  signal: AbortSignal,
) => Promise<ReviewTimelineCommandResponse>;

export class ReviewWorkspaceSessionRuntime {
  private readonly store:
    StoreApi<ReviewWorkspaceRuntimeState>;

  private activeController:
    AbortController | null = null;

  private disposed = false;

  constructor(
    private readonly client:
      ReviewWorkspaceRuntimeClient,
  ) {
    this.store =
      createStore<ReviewWorkspaceRuntimeState>(
        () => clone(INITIAL_STATE),
      );
  }

  getState(): ReviewWorkspaceRuntimeState {
    return clone(
      this.store.getState(),
    );
  }

  subscribe(
    listener:
      ReviewWorkspaceRuntimeListener,
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
    options:
      ReviewWorkspaceRuntimeOpenOptions = {},
  ): Promise<ReviewWorkspaceRuntimeState> {
    this.assertNoTimelineCommandInFlight();

    const normalizedProductionId =
      requireIdentifier(
        productionId,
        "productionId",
      );

    const request = this.beginRequest(
      "opening",
      "open",
      {
        productionId:
          normalizedProductionId,
        sessionId: null,
        session: null,
        snapshot: null,
        pendingCommand: null,
        lastCommand: null,
        lastCommandResponse: null,
      },
    );

    const signal = linkAbortSignals(
      request.controller,
      options.signal,
    );

    try {
      const response =
        await this.client.openSession(
          normalizedProductionId,
          {
            force_refresh:
              options.force_refresh,
            replace_existing:
              options.replace_existing,
          },
          { signal },
        );

      this.completeRequest(
        request.revision,
        {
          status: "ready",
          productionId:
            response.production_id,
          sessionId:
            response.session_id,
          session: response.session,
          snapshot:
            response.snapshot,
        },
      );

      return this.getState();
    } catch (error) {
      this.failRequest(
        request.revision,
        error,
      );
      throw error;
    }
  }

  async refresh(
    options:
      ReviewWorkspaceRuntimeActionOptions = {},
  ): Promise<ReviewWorkspaceRuntimeState> {
    this.assertNoTimelineCommandInFlight();

    const active =
      this.requireActiveSession();

    const request = this.beginRequest(
      "refreshing",
      "refresh",
    );

    const signal = linkAbortSignals(
      request.controller,
      options.signal,
    );

    try {
      const response =
        await this.client.getSnapshot(
          active.productionId,
          active.sessionId,
          { signal },
        );

      this.completeRequest(
        request.revision,
        {
          status: "ready",
          productionId:
            response.production_id,
          sessionId:
            response.session_id,
          session:
            response.snapshot.session,
          snapshot:
            response.snapshot,
        },
      );

      return this.getState();
    } catch (error) {
      this.failRequest(
        request.revision,
        error,
      );
      throw error;
    }
  }

  async reset(
    options:
      ReviewWorkspaceRuntimeActionOptions = {},
  ): Promise<ReviewWorkspaceRuntimeState> {
    this.assertNoTimelineCommandInFlight();

    const active =
      this.requireActiveSession();

    const request = this.beginRequest(
      "resetting",
      "reset",
    );

    const signal = linkAbortSignals(
      request.controller,
      options.signal,
    );

    try {
      const response =
        await this.client.resetSession(
          active.productionId,
          {
            session_id:
              active.sessionId,
          },
          { signal },
        );

      this.completeRequest(
        request.revision,
        {
          status: "ready",
          productionId:
            response.production_id,
          sessionId:
            response.session_id,
          session:
            response.snapshot.session,
          snapshot:
            response.snapshot,
        },
      );

      return this.getState();
    } catch (error) {
      this.failRequest(
        request.revision,
        error,
      );
      throw error;
    }
  }

  async close(
    options:
      ReviewWorkspaceRuntimeActionOptions = {},
  ): Promise<ReviewWorkspaceRuntimeState> {
    this.assertNoTimelineCommandInFlight();

    const active =
      this.requireActiveSession();

    const request = this.beginRequest(
      "closing",
      "close",
    );

    const signal = linkAbortSignals(
      request.controller,
      options.signal,
    );

    try {
      const response =
        await this.client.closeSession(
          active.productionId,
          {
            session_id:
              active.sessionId,
          },
          { signal },
        );

      this.completeRequest(
        request.revision,
        {
          status: "closed",
          productionId:
            response.production_id,
          sessionId:
            response.session_id,
          session: response.state,
          snapshot: null,
        },
      );

      return this.getState();
    } catch (error) {
      this.failRequest(
        request.revision,
        error,
      );
      throw error;
    }
  }

  moveClip(
    input: MoveTimelineClipInput,
    options:
      ReviewWorkspaceRuntimeActionOptions = {},
  ): Promise<ReviewWorkspaceRuntimeState> {
    return this.executeTimelineCommand(
      "move_clip",
      (active, revision, signal) =>
        this.client.moveClip(
          active.productionId,
          {
            ...clone(input),
            session_id:
              active.sessionId,
            expected_revision:
              revision,
          },
          { signal },
        ),
      options,
    );
  }

  trimClipStart(
    input: TrimTimelineClipStartInput,
    options:
      ReviewWorkspaceRuntimeActionOptions = {},
  ): Promise<ReviewWorkspaceRuntimeState> {
    return this.executeTimelineCommand(
      "trim_clip_start",
      (active, revision, signal) =>
        this.client.trimClipStart(
          active.productionId,
          {
            ...clone(input),
            session_id:
              active.sessionId,
            expected_revision:
              revision,
          },
          { signal },
        ),
      options,
    );
  }

  trimClipEnd(
    input: TrimTimelineClipEndInput,
    options:
      ReviewWorkspaceRuntimeActionOptions = {},
  ): Promise<ReviewWorkspaceRuntimeState> {
    return this.executeTimelineCommand(
      "trim_clip_end",
      (active, revision, signal) =>
        this.client.trimClipEnd(
          active.productionId,
          {
            ...clone(input),
            session_id:
              active.sessionId,
            expected_revision:
              revision,
          },
          { signal },
        ),
      options,
    );
  }

  splitClip(
    input: SplitTimelineClipInput,
    options:
      ReviewWorkspaceRuntimeActionOptions = {},
  ): Promise<ReviewWorkspaceRuntimeState> {
    return this.executeTimelineCommand(
      "split_clip",
      (active, revision, signal) =>
        this.client.splitClip(
          active.productionId,
          {
            ...clone(input),
            session_id:
              active.sessionId,
            expected_revision:
              revision,
          },
          { signal },
        ),
      options,
    );
  }

  duplicateClip(
    input: DuplicateTimelineClipInput,
    options:
      ReviewWorkspaceRuntimeActionOptions = {},
  ): Promise<ReviewWorkspaceRuntimeState> {
    return this.executeTimelineCommand(
      "duplicate_clip",
      (active, revision, signal) =>
        this.client.duplicateClip(
          active.productionId,
          {
            ...clone(input),
            session_id:
              active.sessionId,
            expected_revision:
              revision,
          },
          { signal },
        ),
      options,
    );
  }

  deleteClip(
    input: DeleteTimelineClipInput,
    options:
      ReviewWorkspaceRuntimeActionOptions = {},
  ): Promise<ReviewWorkspaceRuntimeState> {
    return this.executeTimelineCommand(
      "delete_clip",
      (active, revision, signal) =>
        this.client.deleteClip(
          active.productionId,
          {
            ...clone(input),
            session_id:
              active.sessionId,
            expected_revision:
              revision,
          },
          { signal },
        ),
      options,
    );
  }

  closeGap(
    input: CloseTimelineGapInput,
    options:
      ReviewWorkspaceRuntimeActionOptions = {},
  ): Promise<ReviewWorkspaceRuntimeState> {
    return this.executeTimelineCommand(
      "close_gap",
      (active, revision, signal) =>
        this.client.closeGap(
          active.productionId,
          {
            ...clone(input),
            session_id:
              active.sessionId,
            expected_revision:
              revision,
          },
          { signal },
        ),
      options,
    );
  }

  undoTimeline(
    options:
      ReviewWorkspaceRuntimeActionOptions = {},
  ): Promise<ReviewWorkspaceRuntimeState> {
    return this.executeTimelineCommand(
      "undo",
      (active, revision, signal) =>
        this.client.undoTimeline(
          active.productionId,
          {
            session_id:
              active.sessionId,
            expected_revision:
              revision,
          },
          { signal },
        ),
      options,
    );
  }

  redoTimeline(
    options:
      ReviewWorkspaceRuntimeActionOptions = {},
  ): Promise<ReviewWorkspaceRuntimeState> {
    return this.executeTimelineCommand(
      "redo",
      (active, revision, signal) =>
        this.client.redoTimeline(
          active.productionId,
          {
            session_id:
              active.sessionId,
            expected_revision:
              revision,
          },
          { signal },
        ),
      options,
    );
  }

  clear(): ReviewWorkspaceRuntimeState {
    this.assertNotDisposed();
    this.cancelActiveRequest();

    const current =
      this.store.getState();

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

  private async executeTimelineCommand(
    operation:
      ReviewTimelineCommandOperation,
    executor: TimelineCommandExecutor,
    options:
      ReviewWorkspaceRuntimeActionOptions,
  ): Promise<ReviewWorkspaceRuntimeState> {
    const active =
      this.requireActiveSession();

    const expectedRevision =
      requireTimelineRevision(
        active.snapshot,
      );

    const request =
      this.beginTimelineCommand(
        operation,
      );

    const signal = linkAbortSignals(
      request.controller,
      options.signal,
    );

    try {
      const response = await executor(
        active,
        expectedRevision,
        signal,
      );

      this.validateCommandResponse(
        response,
        active,
        operation,
      );

      this.completeTimelineCommand(
        request.revision,
        response,
      );

      return this.getState();
    } catch (error) {
      if (
        error instanceof
          ReviewWorkspaceAPIError &&
        error.isRevisionConflict &&
        this.isCurrentRequest(
          request.revision
        )
      ) {
        await this.recoverRevisionConflict(
          request.revision,
          active,
          error,
          signal,
        );
      } else {
        this.failRequest(
          request.revision,
          error,
        );
      }

      throw error;
    }
  }

  private beginTimelineCommand(
    operation:
      ReviewTimelineCommandOperation,
  ): RuntimeRequest {
    this.assertNotDisposed();

    const current =
      this.store.getState();

    if (
      current.pendingOperation !== null
    ) {
      throw new ReviewWorkspaceAPIError(
        "Another Review Workspace operation is already running.",
        {
          code:
            "review_session_conflict",
          status: 409,
          productionId:
            current.productionId,
          sessionId:
            current.sessionId,
        },
      );
    }

    const revision =
      current.requestRevision + 1;

    const controller =
      new AbortController();

    this.activeController =
      controller;

    this.store.setState({
      ...current,
      status: "executing",
      pendingOperation:
        "timeline_command",
      pendingCommand: operation,
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

  private beginRequest(
    status:
      ReviewWorkspaceRuntimeState["status"],
    pendingOperation: Exclude<
      ReviewWorkspaceRuntimeState[
        "pendingOperation"
      ],
      null
    >,
    replacement:
      Partial<ReviewWorkspaceRuntimeState> = {},
  ): RuntimeRequest {
    this.assertNotDisposed();
    this.assertNoTimelineCommandInFlight();
    this.cancelActiveRequest();

    const current =
      this.store.getState();

    const revision =
      current.requestRevision + 1;

    const controller =
      new AbortController();

    this.activeController =
      controller;

    this.store.setState({
      ...current,
      ...clone(replacement),
      status,
      pendingOperation,
      pendingCommand: null,
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
      session:
        ReviewRuntimeSessionState;
      snapshot:
        ReviewRuntimeSessionSnapshot | null;
    },
  ): void {
    const current =
      this.store.getState();

    if (
      revision !==
        current.requestRevision ||
      this.disposed
    ) {
      return;
    }

    this.activeController = null;

    this.store.setState({
      ...current,
      ...clone(replacement),
      pendingOperation: null,
      pendingCommand: null,
      error: null,
      stateRevision:
        current.stateRevision + 1,
      updatedAt: now(),
    });
  }

  private completeTimelineCommand(
    revision: number,
    response:
      ReviewTimelineCommandResponse,
  ): void {
    const current =
      this.store.getState();

    if (
      revision !==
        current.requestRevision ||
      this.disposed
    ) {
      return;
    }

    this.activeController = null;

    this.store.setState({
      ...current,
      status: "ready",
      pendingOperation: null,
      pendingCommand: null,
      lastCommand:
        response.operation,
      lastCommandResponse:
        clone(response),
      productionId:
        response.production_id,
      sessionId:
        response.session_id,
      session:
        clone(response.snapshot.session),
      snapshot:
        clone(response.snapshot),
      error: null,
      stateRevision:
        current.stateRevision + 1,
      updatedAt: now(),
    });
  }

  private async recoverRevisionConflict(
    revision: number,
    active: ActiveSession,
    conflict:
      ReviewWorkspaceAPIError,
    signal: AbortSignal,
  ): Promise<void> {
    try {
      const response =
        await this.client.getSnapshot(
          active.productionId,
          active.sessionId,
          { signal },
        );

      const current =
        this.store.getState();

      if (
        revision !==
          current.requestRevision ||
        this.disposed
      ) {
        return;
      }

      this.activeController = null;

      this.store.setState({
        ...current,
        status: "ready",
        pendingOperation: null,
        pendingCommand: null,
        productionId:
          response.production_id,
        sessionId:
          response.session_id,
        session:
          clone(
            response.snapshot.session,
          ),
        snapshot:
          clone(response.snapshot),
        error:
          normalizeError(conflict),
        stateRevision:
          current.stateRevision + 1,
        updatedAt: now(),
      });
    } catch {
      this.failRequest(
        revision,
        conflict,
      );
    }
  }

  private failRequest(
    revision: number,
    error: unknown,
  ): void {
    const current =
      this.store.getState();

    if (
      revision !==
        current.requestRevision ||
      this.disposed
    ) {
      return;
    }

    this.activeController = null;

    this.store.setState({
      ...current,
      status: "error",
      pendingOperation: null,
      pendingCommand: null,
      error: normalizeError(error),
      stateRevision:
        current.stateRevision + 1,
      updatedAt: now(),
    });
  }

  private validateCommandResponse(
    response:
      ReviewTimelineCommandResponse,
    active: ActiveSession,
    operation:
      ReviewTimelineCommandOperation,
  ): void {
    if (
      response.production_id !==
        active.productionId ||
      response.session_id !==
        active.sessionId ||
      response.operation !== operation
    ) {
      throw new ReviewWorkspaceAPIError(
        "Timeline command response does not match the active session.",
        {
          code: "invalid_response",
          status: 502,
          productionId:
            active.productionId,
          sessionId:
            active.sessionId,
        },
      );
    }
  }

  private requireActiveSession():
    ActiveSession {
    this.assertNotDisposed();

    const state =
      this.store.getState();

    if (
      !state.productionId ||
      !state.sessionId ||
      !state.session ||
      !state.snapshot
    ) {
      throw new ReviewWorkspaceAPIError(
        "Review Workspace session is not open.",
        {
          code:
            "review_session_not_found",
          status: 409,
          productionId:
            state.productionId,
          sessionId:
            state.sessionId,
        },
      );
    }

    if (state.status === "closed") {
      throw new ReviewWorkspaceAPIError(
        "Review Workspace session is closed.",
        {
          code:
            "review_session_not_found",
          status: 409,
          productionId:
            state.productionId,
          sessionId:
            state.sessionId,
        },
      );
    }

    return {
      productionId:
        state.productionId,
      sessionId:
        state.sessionId,
      snapshot:
        clone(state.snapshot),
    };
  }

  private assertNoTimelineCommandInFlight():
    void {
    this.assertNotDisposed();

    const state =
      this.store.getState();

    if (
      state.pendingOperation ===
      "timeline_command"
    ) {
      throw new ReviewWorkspaceAPIError(
        "A timeline command is already running.",
        {
          code:
            "review_session_conflict",
          status: 409,
          productionId:
            state.productionId,
          sessionId:
            state.sessionId,
        },
      );
    }
  }

  private isCurrentRequest(
    revision: number,
  ): boolean {
    return (
      !this.disposed &&
      this.store.getState()
        .requestRevision === revision
    );
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
  if (
    error instanceof
    ReviewWorkspaceAPIError
  ) {
    return {
      name: error.name,
      message: error.message,
      code: error.code,
      status: error.status,
      technicalMessage:
        error.technicalMessage,
      productionId:
        error.productionId,
      sessionId: error.sessionId,
      isRevisionConflict:
        error.isRevisionConflict,
      expectedRevision:
        error.expectedRevision,
      currentRevision:
        error.currentRevision,
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
    isRevisionConflict: false,
    expectedRevision: null,
    currentRevision: null,
  };
}

function requireTimelineRevision(
  snapshot:
    ReviewRuntimeSessionSnapshot,
): number {
  const revision =
    snapshot.timeline.revision;

  if (
    !Number.isInteger(revision) ||
    revision < 1
  ) {
    throw new ReviewWorkspaceAPIError(
      "Active timeline revision is invalid.",
      {
        code: "invalid_response",
        status: 502,
        productionId:
          snapshot.session.production_id,
        sessionId:
          snapshot.session.session_id,
      },
    );
  }

  return revision;
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