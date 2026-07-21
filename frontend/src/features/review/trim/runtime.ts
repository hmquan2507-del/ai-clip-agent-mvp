import {
  projectReviewTimelineClipTrim,
} from "./coordinates";

import {
  REVIEW_TIMELINE_TRIM_CONTRACT_VERSION,
  REVIEW_TIMELINE_TRIM_RUNTIME_CONTRACT_VERSION,
  type ArmReviewTimelineTrimInput,
  type MoveReviewTimelineTrimInput,
  type ReviewTimelineTrimCancelReason,
  type ReviewTimelineTrimEnvironment,
  type ReviewTimelineTrimFailure,
  type ReviewTimelineTrimIntent,
  type ReviewTimelineTrimRuntimeListener,
  type ReviewTimelineTrimRuntimeState,
  type ReviewTimelineTrimSession,
} from "./contracts";
import type {
  ReviewTimelineDragPoint,
} from "../drag";

const DEFAULT_TRIM_THRESHOLD = 3;

const INITIAL_STATE: ReviewTimelineTrimRuntimeState = {
  contractVersion:
    REVIEW_TIMELINE_TRIM_RUNTIME_CONTRACT_VERSION,
  phase: "idle",
  session: null,
  environment: null,
  projection: null,
  commitIntent: null,
  lastCommittedIntent: null,
  cancelReason: null,
  failure: null,
  lastFailure: null,
  pointerDistance: 0,
  stateRevision: 0,
  updatedAt: null,
};

export interface ReviewTimelineTrimSessionRuntimeOptions {
  trimThreshold?: number;
  createSessionId?: () => string;
  now?: () => string;
}

export class ReviewTimelineTrimSessionRuntime {
  private state = clone(INITIAL_STATE);
  private readonly listeners =
    new Set<ReviewTimelineTrimRuntimeListener>();
  private readonly trimThreshold: number;
  private readonly createSessionId: () => string;
  private readonly now: () => string;
  private disposed = false;

  constructor(
    options:
      ReviewTimelineTrimSessionRuntimeOptions = {},
  ) {
    this.trimThreshold = nonNegativeNumber(
      options.trimThreshold ??
        DEFAULT_TRIM_THRESHOLD,
      "trimThreshold",
    );
    this.createSessionId =
      options.createSessionId ??
      defaultSessionId;
    this.now =
      options.now ??
      (() => new Date().toISOString());
  }

  getState(): ReviewTimelineTrimRuntimeState {
    return clone(this.state);
  }

  subscribe(
    listener: ReviewTimelineTrimRuntimeListener,
  ): () => void {
    this.assertNotDisposed();
    this.listeners.add(listener);

    return () => {
      this.listeners.delete(listener);
    };
  }

  arm(
    input: ArmReviewTimelineTrimInput,
  ): ReviewTimelineTrimRuntimeState {
    this.assertNotDisposed();
    this.assertCanArm();

    const environment = normalizeEnvironment(
      input.environment,
    );
    const pointer = normalizePoint(
      input.pointer,
      "pointer",
    );
    const projection =
      projectReviewTimelineClipTrim({
        handle: input.handle,
        source: input.source,
        pointer,
        viewport: environment.viewport,
        timelineDuration:
          environment.timelineDuration,
        fps: environment.fps,
        minimumDuration:
          environment.minimumDuration,
        quantizeToFrame:
          environment.quantizeToFrame,
      });
    const session: ReviewTimelineTrimSession = {
      contractVersion:
        REVIEW_TIMELINE_TRIM_CONTRACT_VERSION,
      sessionId: requireIdentifier(
        this.createSessionId(),
        "sessionId",
      ),
      productionId: requireIdentifier(
        input.productionId,
        "productionId",
      ),
      timelineRevision: positiveInteger(
        input.timelineRevision,
        "timelineRevision",
      ),
      phase: "armed",
      handle: projection.handle,
      source: clone(projection.source),
      pointerOrigin: pointer,
      pointerCurrent: pointer,
    };

    this.replaceState({
      ...INITIAL_STATE,
      phase: "armed",
      session,
      environment,
      projection,
      stateRevision:
        this.state.stateRevision + 1,
      updatedAt: this.now(),
    });

    return this.getState();
  }

  move(
    input: MoveReviewTimelineTrimInput,
  ): ReviewTimelineTrimRuntimeState {
    this.assertNotDisposed();

    const session =
      this.requireInteractiveSession();
    const environment = input.environment
      ? normalizeEnvironment(
          input.environment,
        )
      : requireEnvironment(
          this.state.environment,
        );
    const pointer = normalizePoint(
      input.pointer,
      "pointer",
    );
    const pointerDistance = Math.abs(
      pointer.clientX -
        session.pointerOrigin.clientX,
    );
    const phase =
      this.state.phase === "trimming" ||
      pointerDistance >= this.trimThreshold
        ? "trimming"
        : "armed";
    const nextSession: ReviewTimelineTrimSession = {
      ...session,
      phase,
      pointerCurrent: pointer,
    };
    const projection =
      projectReviewTimelineClipTrim({
        handle: nextSession.handle,
        source: nextSession.source,
        pointer,
        viewport: environment.viewport,
        timelineDuration:
          environment.timelineDuration,
        fps: environment.fps,
        minimumDuration:
          environment.minimumDuration,
        quantizeToFrame:
          environment.quantizeToFrame,
      });

    this.patchState({
      phase,
      session: nextSession,
      environment,
      projection,
      commitIntent: null,
      cancelReason: null,
      failure: null,
      pointerDistance,
    });

    return this.getState();
  }

  prepareCommit(): ReviewTimelineTrimIntent {
    this.assertNotDisposed();

    if (this.state.phase !== "trimming") {
      throw new Error(
        "A trim must cross the movement threshold " +
          "before it can commit.",
      );
    }

    const projection = this.state.projection;
    if (
      !projection?.valid ||
      !projection.trimIntent
    ) {
      throw new Error(
        "The current trim projection cannot commit.",
      );
    }

    const intent = clone(
      projection.trimIntent,
    );
    const session = requireSession(
      this.state.session,
    );

    this.patchState({
      phase: "committing",
      session: {
        ...session,
        phase: "committing",
      },
      commitIntent: intent,
    });

    return clone(intent);
  }

  completeCommit(): ReviewTimelineTrimRuntimeState {
    this.assertNotDisposed();

    if (
      this.state.phase !== "committing" ||
      !this.state.commitIntent
    ) {
      throw new Error(
        "No trim commit is pending.",
      );
    }

    const lastCommittedIntent = clone(
      this.state.commitIntent,
    );

    this.replaceState({
      ...INITIAL_STATE,
      lastCommittedIntent,
      stateRevision:
        this.state.stateRevision + 1,
      updatedAt: this.now(),
    });

    return this.getState();
  }

  failCommit(
    failure: ReviewTimelineTrimFailure,
  ): ReviewTimelineTrimRuntimeState {
    this.assertNotDisposed();

    if (this.state.phase !== "committing") {
      throw new Error(
        "No trim commit is pending.",
      );
    }

    const normalizedFailure =
      normalizeFailure(failure);
    const session = requireSession(
      this.state.session,
    );

    this.patchState({
      phase: "failed",
      session: {
        ...session,
        phase: "failed",
      },
      commitIntent: null,
      cancelReason: null,
      failure: normalizedFailure,
      lastFailure: normalizedFailure,
    });

    return this.getState();
  }

  cancel(
    reason:
      ReviewTimelineTrimCancelReason =
        "pointer_cancelled",
  ): ReviewTimelineTrimRuntimeState {
    this.assertNotDisposed();
    const session = requireSession(
      this.state.session,
    );

    if (this.state.phase === "committing") {
      throw new Error(
        "A committing trim cannot be cancelled.",
      );
    }

    this.patchState({
      phase: "cancelled",
      session: {
        ...session,
        phase: "cancelled",
      },
      commitIntent: null,
      cancelReason: reason,
      failure: null,
    });

    return this.getState();
  }

  reset(): ReviewTimelineTrimRuntimeState {
    this.assertNotDisposed();

    this.replaceState({
      ...INITIAL_STATE,
      stateRevision:
        this.state.stateRevision + 1,
      updatedAt: this.now(),
    });

    return this.getState();
  }

  dispose(): void {
    if (this.disposed) return;

    if (
      this.state.session &&
      this.state.phase !== "committing"
    ) {
      const session = clone(
        this.state.session,
      );
      this.state = {
        ...this.state,
        phase: "cancelled",
        session: {
          ...session,
          phase: "cancelled",
        },
        commitIntent: null,
        cancelReason: "disposed",
        stateRevision:
          this.state.stateRevision + 1,
        updatedAt: this.now(),
      };
    }

    this.listeners.clear();
    this.disposed = true;
  }

  private assertCanArm(): void {
    if (
      this.state.phase !== "idle" &&
      this.state.phase !== "cancelled" &&
      this.state.phase !== "failed"
    ) {
      throw new Error(
        "A timeline trim session is already active.",
      );
    }
  }

  private requireInteractiveSession():
    ReviewTimelineTrimSession {
    if (
      this.state.phase !== "armed" &&
      this.state.phase !== "trimming"
    ) {
      throw new Error(
        "No interactive timeline trim session exists.",
      );
    }

    return requireSession(
      this.state.session,
    );
  }

  private patchState(
    patch: Partial<ReviewTimelineTrimRuntimeState>,
  ): void {
    this.replaceState({
      ...this.state,
      ...clone(patch),
      stateRevision:
        this.state.stateRevision + 1,
      updatedAt: this.now(),
    });
  }

  private replaceState(
    nextState: ReviewTimelineTrimRuntimeState,
  ): void {
    const previousState = clone(
      this.state,
    );
    this.state = clone(nextState);

    for (const listener of this.listeners) {
      listener(
        clone(this.state),
        clone(previousState),
      );
    }
  }

  private assertNotDisposed(): void {
    if (this.disposed) {
      throw new Error(
        "Timeline trim session runtime is disposed.",
      );
    }
  }
}

function normalizeEnvironment(
  environment: ReviewTimelineTrimEnvironment,
): ReviewTimelineTrimEnvironment {
  return {
    viewport: clone(environment.viewport),
    timelineDuration: positiveNumber(
      environment.timelineDuration,
      "timelineDuration",
    ),
    fps: positiveNumber(
      environment.fps,
      "fps",
    ),
    minimumDuration:
      environment.minimumDuration === undefined
        ? undefined
        : positiveNumber(
            environment.minimumDuration,
            "minimumDuration",
          ),
    quantizeToFrame:
      environment.quantizeToFrame,
  };
}

function requireEnvironment(
  environment:
    ReviewTimelineTrimEnvironment | null,
): ReviewTimelineTrimEnvironment {
  if (!environment) {
    throw new Error(
      "Timeline trim environment is unavailable.",
    );
  }
  return clone(environment);
}

function requireSession(
  session: ReviewTimelineTrimSession | null,
): ReviewTimelineTrimSession {
  if (!session) {
    throw new Error(
      "Timeline trim session is unavailable.",
    );
  }
  return clone(session);
}

function normalizePoint(
  point: ReviewTimelineDragPoint,
  name: string,
): ReviewTimelineDragPoint {
  return {
    clientX: finiteNumber(
      point.clientX,
      `${name}.clientX`,
    ),
    clientY: finiteNumber(
      point.clientY,
      `${name}.clientY`,
    ),
  };
}

function normalizeFailure(
  failure: ReviewTimelineTrimFailure,
): ReviewTimelineTrimFailure {
  const message = failure.message.trim();
  if (!message) {
    throw new TypeError(
      "failure.message must not be empty.",
    );
  }

  return {
    code: failure.code,
    message,
    technicalMessage:
      failure.technicalMessage?.trim() ||
      null,
    isRevisionConflict:
      Boolean(failure.isRevisionConflict),
    expectedRevision:
      optionalPositiveInteger(
        failure.expectedRevision,
        "failure.expectedRevision",
      ),
    currentRevision:
      optionalPositiveInteger(
        failure.currentRevision,
        "failure.currentRevision",
      ),
  };
}

function optionalPositiveInteger(
  value: number | null,
  name: string,
): number | null {
  return value === null
    ? null
    : positiveInteger(value, name);
}

function requireIdentifier(
  value: string,
  name: string,
): string {
  const normalized = value.trim();
  if (!normalized) {
    throw new TypeError(
      `${name} must not be empty.`,
    );
  }
  return normalized;
}

function positiveInteger(
  value: number,
  name: string,
): number {
  if (!Number.isInteger(value) || value < 1) {
    throw new TypeError(
      `${name} must be a positive integer.`,
    );
  }
  return value;
}

function nonNegativeNumber(
  value: number,
  name: string,
): number {
  const normalized = finiteNumber(value, name);
  if (normalized < 0) {
    throw new TypeError(
      `${name} must be non-negative.`,
    );
  }
  return normalized;
}

function positiveNumber(
  value: number,
  name: string,
): number {
  const normalized = finiteNumber(value, name);
  if (normalized <= 0) {
    throw new TypeError(
      `${name} must be positive.`,
    );
  }
  return normalized;
}

function finiteNumber(
  value: number,
  name: string,
): number {
  if (!Number.isFinite(value)) {
    throw new TypeError(
      `${name} must be finite.`,
    );
  }
  return value;
}

function defaultSessionId(): string {
  return `trim-${Date.now()}-${Math.random()
    .toString(36)
    .slice(2, 10)}`;
}

function clone<T>(value: T): T {
  return structuredClone(value);
}
