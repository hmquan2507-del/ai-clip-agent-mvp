import {
  clientXToTimelineTime,
  projectReviewTimelineClipMove,
} from "./coordinates";

import {
  REVIEW_TIMELINE_DRAG_CONTRACT_VERSION,
  REVIEW_TIMELINE_DRAG_RUNTIME_CONTRACT_VERSION,
  type ArmReviewTimelineDragInput,
  type MoveReviewTimelineDragInput,
  type ReviewTimelineDragCancelReason,
  type ReviewTimelineDragEnvironment,
  type ReviewTimelineDragFailure,
  type ReviewTimelineDragPoint,
  type ReviewTimelineDragProjection,
  type ReviewTimelineDragRuntimeListener,
  type ReviewTimelineDragRuntimeState,
  type ReviewTimelineDragSession,
  type ReviewTimelineMoveIntent,
} from "./contracts";
import {
  ReviewTimelineSnapRuntime,
} from "./snap-runtime";
import type {
  ReviewTimelineSnapProjector,
  ReviewTimelineSnapResult,
} from "./snap-contracts";

const DEFAULT_DRAG_THRESHOLD = 3;

const INITIAL_STATE: ReviewTimelineDragRuntimeState = {
  contractVersion:
    REVIEW_TIMELINE_DRAG_RUNTIME_CONTRACT_VERSION,
  phase: "idle",
  session: null,
  environment: null,
  projection: null,
  snapResult: null,
  commitIntent: null,
  lastCommittedIntent: null,
  cancelReason: null,
  failure: null,
  lastFailure: null,
  pointerDistance: 0,
  stateRevision: 0,
  updatedAt: null,
};

export interface ReviewTimelineDragSessionRuntimeOptions {
  dragThreshold?: number;
  createSessionId?: () => string;
  now?: () => string;
  snapProjector?: ReviewTimelineSnapProjector;
}

export class ReviewTimelineDragSessionRuntime {
  private state = clone(INITIAL_STATE);
  private readonly listeners =
    new Set<ReviewTimelineDragRuntimeListener>();
  private readonly dragThreshold: number;
  private readonly createSessionId: () => string;
  private readonly now: () => string;
  private readonly snapProjector:
    ReviewTimelineSnapProjector;
  private disposed = false;

  constructor(
    options:
      ReviewTimelineDragSessionRuntimeOptions = {},
  ) {
    this.dragThreshold = nonNegativeNumber(
      options.dragThreshold ??
        DEFAULT_DRAG_THRESHOLD,
      "dragThreshold",
    );
    this.createSessionId =
      options.createSessionId ??
      defaultSessionId;
    this.now =
      options.now ??
      (() => new Date().toISOString());
    this.snapProjector =
      options.snapProjector ??
      new ReviewTimelineSnapRuntime();
  }

  getState(): ReviewTimelineDragRuntimeState {
    return clone(this.state);
  }

  subscribe(
    listener: ReviewTimelineDragRuntimeListener,
  ): () => void {
    this.assertNotDisposed();
    this.listeners.add(listener);

    return () => {
      this.listeners.delete(listener);
    };
  }

  arm(
    input: ArmReviewTimelineDragInput,
  ): ReviewTimelineDragRuntimeState {
    this.assertNotDisposed();
    this.assertCanArm();

    const environment =
      normalizeEnvironment(input.environment);
    const source = clone(input.source);
    const pointer = normalizePoint(
      input.pointer,
      "pointer",
    );
    const productionId = requireIdentifier(
      input.productionId,
      "productionId",
    );
    const timelineRevision = positiveInteger(
      input.timelineRevision,
      "timelineRevision",
    );
    const grabOffsetTime =
      input.grabOffsetTime === undefined
        ? calculateGrabOffsetTime(
            pointer,
            source.startTime,
            source.duration,
            environment,
          )
        : clamp(
            finiteNumber(
              input.grabOffsetTime,
              "grabOffsetTime",
            ),
            0,
            positiveNumber(
              source.duration,
              "source.duration",
            ),
          );
    const session: ReviewTimelineDragSession = {
      contractVersion:
        REVIEW_TIMELINE_DRAG_CONTRACT_VERSION,
      sessionId: requireIdentifier(
        this.createSessionId(),
        "sessionId",
      ),
      productionId,
      timelineRevision,
      phase: "armed",
      source,
      pointerOrigin: pointer,
      pointerCurrent: pointer,
      grabOffsetTime,
    };
    const projected = this.projectMove(
      projectReviewTimelineClipMove({
        source,
        pointer,
        grabOffsetTime,
        viewport: environment.viewport,
        duration:
          environment.timelineDuration,
        fps: environment.fps,
        lanes: environment.lanes,
        quantizeToFrame:
          environment.quantizeToFrame,
      }),
      environment,
    );

    this.replaceState({
      ...INITIAL_STATE,
      phase: "armed",
      session,
      environment,
      projection: projected.projection,
      snapResult: projected.snapResult,
      stateRevision:
        this.state.stateRevision + 1,
      updatedAt: this.now(),
    });

    return this.getState();
  }

  move(
    input: MoveReviewTimelineDragInput,
  ): ReviewTimelineDragRuntimeState {
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
    const pointerDistance = distance(
      session.pointerOrigin,
      pointer,
    );
    const phase =
      this.state.phase === "dragging" ||
      pointerDistance >= this.dragThreshold
        ? "dragging"
        : "armed";
    const nextSession: ReviewTimelineDragSession = {
      ...session,
      phase,
      pointerCurrent: pointer,
    };
    const projected = this.projectMove(
      projectReviewTimelineClipMove({
        source: nextSession.source,
        pointer,
        grabOffsetTime:
          nextSession.grabOffsetTime,
        viewport: environment.viewport,
        duration:
          environment.timelineDuration,
        fps: environment.fps,
        lanes: environment.lanes,
        quantizeToFrame:
          environment.quantizeToFrame,
      }),
      environment,
    );

    this.patchState({
      phase,
      session: nextSession,
      environment,
      projection: projected.projection,
      snapResult: projected.snapResult,
      commitIntent: null,
      cancelReason: null,
      pointerDistance,
    });

    return this.getState();
  }

  prepareCommit(): ReviewTimelineMoveIntent {
    this.assertNotDisposed();

    if (this.state.phase !== "dragging") {
      throw new Error(
        "A drag must cross the movement threshold " +
          "before it can commit.",
      );
    }

    const projection = this.state.projection;
    if (
      !projection?.valid ||
      !projection.moveIntent
    ) {
      throw new Error(
        "The current drag projection cannot commit.",
      );
    }

    const intent = clone(
      projection.moveIntent,
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

  completeCommit(): ReviewTimelineDragRuntimeState {
    this.assertNotDisposed();

    if (
      this.state.phase !== "committing" ||
      !this.state.commitIntent
    ) {
      throw new Error(
        "No drag commit is pending.",
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
    failure: ReviewTimelineDragFailure,
  ): ReviewTimelineDragRuntimeState {
    this.assertNotDisposed();

    if (this.state.phase !== "committing") {
      throw new Error(
        "No drag commit is pending.",
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
      ReviewTimelineDragCancelReason =
        "pointer_cancelled",
  ): ReviewTimelineDragRuntimeState {
    this.assertNotDisposed();
    const session = requireSession(
      this.state.session,
    );

    if (this.state.phase === "committing") {
      throw new Error(
        "A committing drag cannot be cancelled.",
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

  reset(): ReviewTimelineDragRuntimeState {
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
    if (this.disposed) {
      return;
    }

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
        "A timeline drag session is already active.",
      );
    }
  }

  private projectMove(
    projection: ReviewTimelineDragProjection,
    environment: ReviewTimelineDragEnvironment,
  ): {
    projection: ReviewTimelineDragProjection;
    snapResult: ReviewTimelineSnapResult | null;
  } {
    if (
      !projection.valid ||
      !projection.targetTrackId ||
      !projection.moveIntent ||
      !environment.snap
    ) {
      return {
        projection: clone(projection),
        snapResult: null,
      };
    }

    const snapResult =
      this.snapProjector.project({
        sourceClipId:
          projection.source.clipId,
        targetTrackId:
          projection.targetTrackId,
        projectedStartTime:
          projection.projectedStartTime,
        clipDuration:
          projection.source.duration,
        timelineDuration:
          environment.timelineDuration,
        fps: environment.fps,
        viewport: environment.viewport,
        context: environment.snap,
      });

    return {
      projection: {
        ...clone(projection),
        projectedStartTime:
          snapResult.snappedStartTime,
        projectedEndTime:
          snapResult.snappedEndTime,
        moveIntent: {
          ...clone(projection.moveIntent),
          newStartTime:
            snapResult.snappedStartTime,
        },
      },
      snapResult: clone(snapResult),
    };
  }

  private requireInteractiveSession():
    ReviewTimelineDragSession {
    if (
      this.state.phase !== "armed" &&
      this.state.phase !== "dragging"
    ) {
      throw new Error(
        "No interactive timeline drag session exists.",
      );
    }

    return requireSession(
      this.state.session,
    );
  }

  private patchState(
    patch: Partial<ReviewTimelineDragRuntimeState>,
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
    nextState: ReviewTimelineDragRuntimeState,
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
        "Timeline drag session runtime is disposed.",
      );
    }
  }
}

function calculateGrabOffsetTime(
  pointer: ReviewTimelineDragPoint,
  sourceStartTime: number,
  sourceDuration: number,
  environment: ReviewTimelineDragEnvironment,
): number {
  const pointerTime = clientXToTimelineTime(
    pointer.clientX,
    environment.viewport,
    environment.timelineDuration,
  );

  return clamp(
    pointerTime -
      nonNegativeNumber(
        sourceStartTime,
        "source.startTime",
      ),
    0,
    positiveNumber(
      sourceDuration,
      "source.duration",
    ),
  );
}

function normalizeEnvironment(
  environment: ReviewTimelineDragEnvironment,
): ReviewTimelineDragEnvironment {
  return {
    viewport: clone(environment.viewport),
    timelineDuration: nonNegativeNumber(
      environment.timelineDuration,
      "timelineDuration",
    ),
    fps: positiveNumber(
      environment.fps,
      "fps",
    ),
    lanes: clone(environment.lanes),
    quantizeToFrame:
      environment.quantizeToFrame,
    snap: environment.snap
      ? clone(environment.snap)
      : undefined,
  };
}

function requireEnvironment(
  environment:
    ReviewTimelineDragEnvironment | null,
): ReviewTimelineDragEnvironment {
  if (!environment) {
    throw new Error(
      "Timeline drag environment is unavailable.",
    );
  }

  return clone(environment);
}

function requireSession(
  session: ReviewTimelineDragSession | null,
): ReviewTimelineDragSession {
  if (!session) {
    throw new Error(
      "Timeline drag session is unavailable.",
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
  failure: ReviewTimelineDragFailure,
): ReviewTimelineDragFailure {
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
  if (value === null) {
    return null;
  }

  return positiveInteger(value, name);
}

function distance(
  origin: ReviewTimelineDragPoint,
  current: ReviewTimelineDragPoint,
): number {
  return Math.hypot(
    current.clientX - origin.clientX,
    current.clientY - origin.clientY,
  );
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
  if (
    !Number.isInteger(value) ||
    value < 1
  ) {
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
  const normalized = finiteNumber(
    value,
    name,
  );

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
  const normalized = finiteNumber(
    value,
    name,
  );

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

function clamp(
  value: number,
  minimum: number,
  maximum: number,
): number {
  return Math.min(
    Math.max(value, minimum),
    maximum,
  );
}

function defaultSessionId(): string {
  if (
    typeof globalThis.crypto?.randomUUID ===
    "function"
  ) {
    return globalThis.crypto.randomUUID();
  }

  return (
    "drag-" +
    Date.now().toString(36) +
    "-" +
    Math.random().toString(36).slice(2)
  );
}

function clone<T>(value: T): T {
  return structuredClone(value);
}
