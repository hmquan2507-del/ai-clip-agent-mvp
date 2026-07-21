import {
  REVIEW_TIMELINE_VIEWPORT_CONTRACT_VERSION,
  type ReviewTimelineViewportLimits,
  type ReviewTimelineViewportListener,
  type ReviewTimelineViewportMetrics,
  type ReviewTimelineViewportState,
} from "./contracts";

const DEFAULT_LIMITS: ReviewTimelineViewportLimits = {
  minimumZoom: 1,
  maximumZoom: 8,
  zoomStep: 0.5,
};

const INITIAL_STATE: ReviewTimelineViewportState = {
  contractVersion:
    REVIEW_TIMELINE_VIEWPORT_CONTRACT_VERSION,
  zoom: 1,
  scrollLeft: 0,
  duration: 0,
  viewportWidth: 1,
  baseContentWidth: 1,
  contentWidth: 1,
  visibleStartTime: 0,
  visibleEndTime: 0,
  canZoomIn: true,
  canZoomOut: false,
  stateRevision: 0,
  updatedAt: null,
};

export interface ReviewTimelineViewportRuntimeOptions {
  limits?: Partial<ReviewTimelineViewportLimits>;
  now?: () => string;
}

export class ReviewTimelineViewportRuntime {
  private state = clone(INITIAL_STATE);
  private readonly limits:
    ReviewTimelineViewportLimits;
  private readonly listeners =
    new Set<ReviewTimelineViewportListener>();
  private readonly now: () => string;
  private disposed = false;

  constructor(
    options: ReviewTimelineViewportRuntimeOptions = {},
  ) {
    this.limits = normalizeLimits({
      ...DEFAULT_LIMITS,
      ...options.limits,
    });
    this.now =
      options.now ??
      (() => new Date().toISOString());
  }

  getState(): ReviewTimelineViewportState {
    return clone(this.state);
  }

  subscribe(
    listener: ReviewTimelineViewportListener,
  ): () => void {
    this.assertActive();
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }

  synchronize(
    metrics: ReviewTimelineViewportMetrics,
  ): ReviewTimelineViewportState {
    this.assertActive();
    const duration = nonNegative(
      metrics.duration,
      "duration",
    );
    const viewportWidth = positive(
      metrics.viewportWidth,
      "viewportWidth",
    );
    const baseContentWidth = Math.max(
      viewportWidth,
      positive(
        metrics.baseContentWidth,
        "baseContentWidth",
      ),
    );
    const anchorTime = this.centerTime();

    return this.commit({
      ...this.state,
      duration,
      viewportWidth,
      baseContentWidth,
      scrollLeft: scrollForAnchor(
        anchorTime,
        viewportWidth / 2,
        duration,
        baseContentWidth * this.state.zoom,
        viewportWidth,
      ),
    });
  }

  setScrollLeft(
    scrollLeft: number,
  ): ReviewTimelineViewportState {
    this.assertActive();
    return this.commit({
      ...this.state,
      scrollLeft: finite(
        scrollLeft,
        "scrollLeft",
      ),
    });
  }

  zoomIn(): ReviewTimelineViewportState {
    return this.setZoom(
      this.state.zoom +
        this.limits.zoomStep,
    );
  }

  zoomOut(): ReviewTimelineViewportState {
    return this.setZoom(
      this.state.zoom -
        this.limits.zoomStep,
    );
  }

  setZoom(
    zoom: number,
    anchorTime = this.centerTime(),
    anchorViewportX =
      this.state.viewportWidth / 2,
  ): ReviewTimelineViewportState {
    this.assertActive();
    const nextZoom = clamp(
      finite(zoom, "zoom"),
      this.limits.minimumZoom,
      this.limits.maximumZoom,
    );
    const contentWidth =
      this.state.baseContentWidth * nextZoom;

    return this.commit({
      ...this.state,
      zoom: nextZoom,
      scrollLeft: scrollForAnchor(
        anchorTime,
        anchorViewportX,
        this.state.duration,
        contentWidth,
        this.state.viewportWidth,
      ),
    });
  }

  fit(): ReviewTimelineViewportState {
    this.assertActive();
    return this.commit({
      ...this.state,
      zoom: this.limits.minimumZoom,
      scrollLeft: 0,
    });
  }

  reset(): ReviewTimelineViewportState {
    this.assertActive();
    return this.commit({
      ...INITIAL_STATE,
      canZoomIn:
        this.limits.minimumZoom <
        this.limits.maximumZoom,
    });
  }

  dispose(): void {
    if (this.disposed) return;
    this.listeners.clear();
    this.disposed = true;
  }

  private centerTime(): number {
    if (
      this.state.duration <= 0 ||
      this.state.contentWidth <= 0
    ) {
      return 0;
    }
    return clamp(
      (
        this.state.scrollLeft +
        this.state.viewportWidth / 2
      ) /
        this.state.contentWidth *
        this.state.duration,
      0,
      this.state.duration,
    );
  }

  private commit(
    input: ReviewTimelineViewportState,
  ): ReviewTimelineViewportState {
    const contentWidth = Math.max(
      input.viewportWidth,
      input.baseContentWidth * input.zoom,
    );
    const maximumScroll = Math.max(
      0,
      contentWidth - input.viewportWidth,
    );
    const scrollLeft = clamp(
      input.scrollLeft,
      0,
      maximumScroll,
    );
    const visibleStartTime =
      input.duration <= 0
        ? 0
        : scrollLeft /
          contentWidth *
          input.duration;
    const visibleEndTime =
      input.duration <= 0
        ? 0
        : clamp(
            (
              scrollLeft +
              input.viewportWidth
            ) /
              contentWidth *
              input.duration,
            0,
            input.duration,
          );
    const previous = clone(this.state);

    this.state = {
      ...clone(input),
      contractVersion:
        REVIEW_TIMELINE_VIEWPORT_CONTRACT_VERSION,
      contentWidth,
      scrollLeft,
      visibleStartTime,
      visibleEndTime,
      canZoomIn:
        input.zoom <
        this.limits.maximumZoom,
      canZoomOut:
        input.zoom >
        this.limits.minimumZoom,
      stateRevision:
        this.state.stateRevision + 1,
      updatedAt: this.now(),
    };

    for (const listener of this.listeners) {
      listener(
        clone(this.state),
        clone(previous),
      );
    }
    return this.getState();
  }

  private assertActive(): void {
    if (this.disposed) {
      throw new Error(
        "Timeline viewport runtime is disposed.",
      );
    }
  }
}

function scrollForAnchor(
  anchorTime: number,
  anchorViewportX: number,
  duration: number,
  contentWidth: number,
  viewportWidth: number,
): number {
  if (duration <= 0) return 0;
  const contentX =
    clamp(anchorTime, 0, duration) /
    duration *
    contentWidth;
  return clamp(
    contentX - clamp(
      anchorViewportX,
      0,
      viewportWidth,
    ),
    0,
    Math.max(0, contentWidth - viewportWidth),
  );
}

function normalizeLimits(
  limits: ReviewTimelineViewportLimits,
): ReviewTimelineViewportLimits {
  const minimumZoom = positive(
    limits.minimumZoom,
    "minimumZoom",
  );
  const maximumZoom = positive(
    limits.maximumZoom,
    "maximumZoom",
  );
  if (maximumZoom < minimumZoom) {
    throw new Error(
      "maximumZoom must be greater than or equal to minimumZoom.",
    );
  }
  return {
    minimumZoom,
    maximumZoom,
    zoomStep: positive(
      limits.zoomStep,
      "zoomStep",
    ),
  };
}

function finite(value: number, name: string): number {
  if (!Number.isFinite(value)) {
    throw new Error(`${name} must be finite.`);
  }
  return value;
}

function positive(value: number, name: string): number {
  const normalized = finite(value, name);
  if (normalized <= 0) {
    throw new Error(`${name} must be greater than zero.`);
  }
  return normalized;
}

function nonNegative(
  value: number,
  name: string,
): number {
  const normalized = finite(value, name);
  if (normalized < 0) {
    throw new Error(`${name} must not be negative.`);
  }
  return normalized;
}

function clamp(
  value: number,
  minimum: number,
  maximum: number,
): number {
  return Math.min(
    maximum,
    Math.max(minimum, value),
  );
}

function clone<T>(value: T): T {
  return structuredClone(value);
}
