import {
  PLAYHEAD_RUNTIME_CONTRACT_VERSION,
  type PlayheadConfiguration,
  type PlayheadEvent,
  type PlayheadEventType,
  type PlayheadListener,
  type PlayheadPlaybackSnapshot,
  type PlayheadSeekRequester,
  type PlayheadSnapshot,
} from "../contracts";
import { assertPositiveNumber, clampPlaybackTime } from "./playback-time-model";
import {
  clampScrollOffset,
  coordinateFromFrame,
  coordinateFromTime,
  normalizePixelsPerSecond,
  normalizeViewportWidth,
  totalTimelineWidth,
  viewportPixelToTime,
} from "./playhead-coordinate-model";

export interface PlayheadRuntimeOptions {
  now?: () => string;
  requestSeek?: PlayheadSeekRequester;
}

export class PlayheadRuntime {
  private state: PlayheadSnapshot;
  private readonly initial: Pick<PlayheadSnapshot, "timeSeconds" | "pixelsPerSecond" | "viewportWidth" | "scrollOffset">;
  private readonly listeners = new Set<PlayheadListener>();
  private readonly now: () => string;
  private readonly requestSeek?: PlayheadSeekRequester;
  private dragOrigin: PlayheadSnapshot | null = null;
  private disposed = false;

  constructor(configuration: PlayheadConfiguration, options: PlayheadRuntimeOptions = {}) {
    const durationSeconds = Math.max(0, configuration.duration);
    const fps = assertPositiveNumber(configuration.fps, "fps");
    const pixelsPerSecond = normalizePixelsPerSecond(configuration.pixelsPerSecond ?? 100);
    const viewportWidth = normalizeViewportWidth(configuration.viewportWidth ?? 0);
    const scrollOffset = clampScrollOffset(configuration.scrollOffset ?? 0, durationSeconds, pixelsPerSecond, viewportWidth);
    const coordinate = coordinateFromTime(configuration.initialTime ?? 0, durationSeconds, fps, pixelsPerSecond, scrollOffset);
    this.now = options.now ?? (() => new Date().toISOString());
    this.requestSeek = options.requestSeek;
    this.state = {
      contractVersion: PLAYHEAD_RUNTIME_CONTRACT_VERSION,
      status: "idle",
      ...coordinate,
      durationSeconds,
      fps,
      pixelsPerSecond,
      viewportWidth,
      scrollOffset,
      totalTimelineWidth: totalTimelineWidth(durationSeconds, pixelsPerSecond),
      isDragging: false,
      stateRevision: 0,
      updatedAt: null,
    };
    this.initial = { timeSeconds: this.state.timeSeconds, pixelsPerSecond, viewportWidth, scrollOffset };
  }

  getSnapshot(): PlayheadSnapshot { return cloneSnapshot(this.state); }
  getState(): PlayheadSnapshot { return this.getSnapshot(); }

  subscribe(listener: PlayheadListener): () => void {
    this.assertActive();
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  ready(): PlayheadSnapshot {
    this.assertActive();
    return this.commit({ ...this.state, status: "ready", isDragging: false }, "ready");
  }

  setViewport(viewportWidth: number): PlayheadSnapshot {
    this.assertActive();
    const width = normalizeViewportWidth(viewportWidth);
    const scrollOffset = clampScrollOffset(this.state.scrollOffset, this.state.durationSeconds, this.state.pixelsPerSecond, width);
    return this.commit(this.withCoordinate({ ...this.state, viewportWidth: width, scrollOffset }), "viewport-changed");
  }

  setZoom(pixelsPerSecond: number): PlayheadSnapshot {
    this.assertActive();
    const zoom = normalizePixelsPerSecond(pixelsPerSecond);
    const scrollOffset = clampScrollOffset(this.state.scrollOffset, this.state.durationSeconds, zoom, this.state.viewportWidth);
    return this.commit(this.withCoordinate({ ...this.state, pixelsPerSecond: zoom, scrollOffset, totalTimelineWidth: totalTimelineWidth(this.state.durationSeconds, zoom) }), "zoom-changed");
  }

  setScrollOffset(scrollOffset: number): PlayheadSnapshot {
    this.assertActive();
    const bounded = clampScrollOffset(scrollOffset, this.state.durationSeconds, this.state.pixelsPerSecond, this.state.viewportWidth);
    return this.commit(this.withCoordinate({ ...this.state, scrollOffset: bounded }), "scroll-changed");
  }

  moveToTime(timeSeconds: number): PlayheadSnapshot {
    this.assertActive();
    return this.commit(this.withTime(clampPlaybackTime(timeSeconds, this.state.durationSeconds), "synced"), "moved");
  }

  moveToFrame(frame: number): PlayheadSnapshot {
    this.assertActive();
    const coordinate = coordinateFromFrame(frame, this.state.durationSeconds, this.state.fps, this.state.pixelsPerSecond, this.state.scrollOffset);
    return this.commit({ ...this.state, ...coordinate, status: "synced" }, "moved");
  }

  moveToPixel(viewportPixel: number): PlayheadSnapshot {
    this.assertActive();
    const time = viewportPixelToTime(viewportPixel, this.state.durationSeconds, this.state.pixelsPerSecond, this.state.scrollOffset);
    return this.commit(this.withTime(time, "synced"), "moved");
  }

  beginDrag(): PlayheadSnapshot {
    this.assertActive();
    if (this.state.isDragging) return this.getSnapshot();
    this.dragOrigin = cloneSnapshot(this.state);
    return this.commit({ ...this.state, status: "dragging", isDragging: true }, "drag-started");
  }

  dragToPixel(viewportPixel: number): PlayheadSnapshot {
    this.assertActive();
    if (!this.state.isDragging) throw new Error("Playhead drag has not started.");
    const time = viewportPixelToTime(viewportPixel, this.state.durationSeconds, this.state.pixelsPerSecond, this.state.scrollOffset);
    return this.commit(this.withTime(time, "dragging", true), "drag-previewed");
  }

  endDrag(): PlayheadSnapshot {
    this.assertActive();
    if (!this.state.isDragging) return this.getSnapshot();
    const committedTime = this.state.timeSeconds;
    this.dragOrigin = null;
    const result = this.commit({ ...this.state, status: "synced", isDragging: false }, "drag-ended");
    this.requestSeek?.(committedTime);
    return result;
  }

  cancelDrag(): PlayheadSnapshot {
    this.assertActive();
    if (!this.state.isDragging || !this.dragOrigin) return this.getSnapshot();
    const origin = this.dragOrigin;
    this.dragOrigin = null;
    return this.commit({ ...origin, status: "synced", isDragging: false, stateRevision: this.state.stateRevision, updatedAt: this.state.updatedAt }, "drag-cancelled");
  }

  syncFromPlayback(snapshot: PlayheadPlaybackSnapshot): PlayheadSnapshot {
    this.assertActive();
    if (this.state.isDragging) return this.getSnapshot();
    const time = clampPlaybackTime(snapshot.currentTime, this.state.durationSeconds);
    if (time === this.state.timeSeconds && this.state.status === "synced") return this.getSnapshot();
    return this.commit(this.withTime(time, "synced"), "playback-synced");
  }

  reset(): PlayheadSnapshot {
    this.assertActive();
    this.dragOrigin = null;
    const scrollOffset = clampScrollOffset(this.initial.scrollOffset, this.state.durationSeconds, this.initial.pixelsPerSecond, this.initial.viewportWidth);
    const base = {
      ...this.state,
      status: "idle" as const,
      pixelsPerSecond: this.initial.pixelsPerSecond,
      viewportWidth: this.initial.viewportWidth,
      scrollOffset,
      totalTimelineWidth: totalTimelineWidth(this.state.durationSeconds, this.initial.pixelsPerSecond),
      isDragging: false,
    };
    return this.commit(this.withTime(this.initial.timeSeconds, "idle", false, base), "reset");
  }

  dispose(): void {
    if (this.disposed) return;
    this.dragOrigin = null;
    this.listeners.clear();
    this.disposed = true;
    this.state = { ...this.state, status: "disposed", isDragging: false, updatedAt: this.now() };
  }

  private withCoordinate(state: PlayheadSnapshot): PlayheadSnapshot {
    const coordinate = coordinateFromTime(state.timeSeconds, state.durationSeconds, state.fps, state.pixelsPerSecond, state.scrollOffset);
    return { ...state, ...coordinate, totalTimelineWidth: totalTimelineWidth(state.durationSeconds, state.pixelsPerSecond) };
  }

  private withTime(time: number, status: PlayheadSnapshot["status"], isDragging = this.state.isDragging, base = this.state): PlayheadSnapshot {
    const coordinate = coordinateFromTime(time, base.durationSeconds, base.fps, base.pixelsPerSecond, base.scrollOffset);
    return { ...base, ...coordinate, status, isDragging };
  }

  private commit(candidate: PlayheadSnapshot, eventType: PlayheadEventType): PlayheadSnapshot {
    const previous = cloneSnapshot(this.state);
    const occurredAt = this.now();
    this.state = { ...candidate, stateRevision: this.state.stateRevision + 1, updatedAt: occurredAt };
    const current = cloneSnapshot(this.state);
    const event: PlayheadEvent = { type: eventType, stateRevision: current.stateRevision, occurredAt };
    for (const listener of this.listeners) listener(cloneSnapshot(current), cloneSnapshot(previous), { ...event });
    return current;
  }

  private assertActive(): void {
    if (this.disposed) throw new Error("Playhead runtime has been disposed.");
  }
}

export function createPlayheadRuntime(configuration: PlayheadConfiguration, options: PlayheadRuntimeOptions = {}): PlayheadRuntime {
  return new PlayheadRuntime(configuration, options);
}

function cloneSnapshot(snapshot: PlayheadSnapshot): PlayheadSnapshot { return { ...snapshot }; }
