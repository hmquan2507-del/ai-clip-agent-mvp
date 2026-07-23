import type {
  PlaybackDirection,
  PlaybackSessionConfiguration,
  PlaybackSessionState,
  ProfessionalPlaybackConfiguration,
  ProfessionalPlaybackEvent,
  ProfessionalPlaybackEventType,
  ProfessionalPlaybackHistoryPort,
  ProfessionalPlaybackListener,
  ProfessionalPlaybackLoopMode,
  ProfessionalPlaybackMetrics,
  ProfessionalPlaybackRange,
  ProfessionalPlaybackSnapshot,
} from "../contracts";
import { PROFESSIONAL_PLAYBACK_CONTRACT_VERSION } from "../contracts";
import { PlaybackSessionRuntime } from "./playback-session-runtime";
import { PlaybackClockRuntime } from "./playback-clock-runtime";
import { PlaybackLoopRuntime } from "./playback-loop-runtime";
import { PlaybackSpeedRuntime } from "./playback-speed-runtime";
import { PlaybackBufferRuntime } from "./playback-buffer-runtime";
import { PlaybackCacheRuntime } from "./playback-cache-runtime";

export interface PlaybackEngineRuntimeOptions {
  readonly now?: () => string;
  readonly history?: ProfessionalPlaybackHistoryPort;
}

export class PlaybackEngineRuntime {
  readonly session: PlaybackSessionRuntime;
  readonly clock = new PlaybackClockRuntime();
  readonly speed = new PlaybackSpeedRuntime();
  readonly loop = new PlaybackLoopRuntime();
  readonly buffer: PlaybackBufferRuntime;
  readonly cache: PlaybackCacheRuntime;

  private readonly listeners = new Set<ProfessionalPlaybackListener>();
  private readonly now: () => string;
  private readonly history?: ProfessionalPlaybackHistoryPort;
  private loopMode: ProfessionalPlaybackLoopMode;
  private loopRange: ProfessionalPlaybackRange | null;
  private inPoint: number | null = null;
  private outPoint: number | null = null;
  private followPlayhead: boolean;
  private autoScroll: boolean;
  private loopCount = 0;
  private renderedFrames = 0;
  private droppedFrames = 0;
  private averageFrameTimeMs = 0;
  private playbackLatencyMs = 0;
  private stateRevision = 0;
  private updatedAt: string | null = null;
  private disposed = false;

  constructor(
    configuration: ProfessionalPlaybackConfiguration,
    options: PlaybackEngineRuntimeOptions = {},
  ) {
    const sessionConfiguration: PlaybackSessionConfiguration = {
      duration: configuration.duration,
      fps: configuration.fps,
      initialTime: configuration.initialTime,
      initialSpeed: configuration.initialSpeed,
      initialDirection: configuration.initialDirection,
      initialLoop: configuration.initialLoopMode === "timeline",
    };
    this.session = new PlaybackSessionRuntime(sessionConfiguration, { now: options.now });
    this.buffer = new PlaybackBufferRuntime(
      configuration.bufferTargetSeconds,
      configuration.lowBufferThresholdSeconds,
    );
    this.cache = new PlaybackCacheRuntime(configuration.cacheCapacity);
    this.loopMode = configuration.initialLoopMode ?? "off";
    this.loopRange = configuration.initialLoopRange
      ? { ...configuration.initialLoopRange }
      : null;
    this.followPlayhead = configuration.followPlayhead ?? true;
    this.autoScroll = configuration.autoScroll ?? true;
    this.now = options.now ?? (() => new Date().toISOString());
    this.history = options.history;
  }

  getSnapshot(): ProfessionalPlaybackSnapshot {
    return {
      contractVersion: PROFESSIONAL_PLAYBACK_CONTRACT_VERSION,
      status: mapStatus(this.session.getSnapshot()),
      session: this.session.getSnapshot(),
      loopMode: this.loopMode,
      loopRange: this.loopRange ? { ...this.loopRange } : null,
      inPoint: this.inPoint,
      outPoint: this.outPoint,
      followPlayhead: this.followPlayhead,
      autoScroll: this.autoScroll,
      buffer: this.buffer.getSnapshot(this.session.getSnapshot().currentTime),
      cache: this.cache.getSnapshot(),
      metrics: this.getMetrics(),
      stateRevision: this.stateRevision,
      updatedAt: this.updatedAt,
    };
  }

  subscribe(listener: ProfessionalPlaybackListener): () => void {
    this.assertActive();
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  ready(): ProfessionalPlaybackSnapshot {
    this.session.ready();
    return this.commit("ready");
  }

  play(): ProfessionalPlaybackSnapshot {
    this.session.play();
    this.clock.reset();
    return this.commit("played");
  }

  pause(): ProfessionalPlaybackSnapshot {
    this.session.pause();
    return this.commit("paused");
  }

  stop(): ProfessionalPlaybackSnapshot {
    this.session.stop();
    return this.commit("stopped");
  }

  togglePlayPause(): ProfessionalPlaybackSnapshot {
    return this.session.getSnapshot().playing ? this.pause() : this.play();
  }

  seek(time: number): ProfessionalPlaybackSnapshot {
    this.session.seek(time);
    return this.commit("seeked");
  }

  stepForward(frames = 1): ProfessionalPlaybackSnapshot {
    this.session.stepForward(frames);
    return this.commit("stepped");
  }

  stepBackward(frames = 1): ProfessionalPlaybackSnapshot {
    this.session.stepBackward(frames);
    return this.commit("stepped");
  }

  setSpeed(speed: number): ProfessionalPlaybackSnapshot {
    this.session.setSpeed(this.speed.normalize(speed));
    return this.commit("speed-changed");
  }

  setDirection(direction: PlaybackDirection): ProfessionalPlaybackSnapshot {
    this.session.setDirection(direction);
    return this.commit("direction-changed");
  }

  j(): ProfessionalPlaybackSnapshot {
    const current = this.session.getSnapshot();
    this.session.setDirection(-1);
    this.session.setSpeed(this.speed.nextShuttleSpeed(current, -1));
    this.session.play();
    this.clock.reset();
    return this.commit("played");
  }

  k(): ProfessionalPlaybackSnapshot {
    this.session.pause();
    this.session.setSpeed(1);
    return this.commit("paused");
  }

  l(): ProfessionalPlaybackSnapshot {
    const current = this.session.getSnapshot();
    this.session.setDirection(1);
    this.session.setSpeed(this.speed.nextShuttleSpeed(current, 1));
    this.session.play();
    this.clock.reset();
    return this.commit("played");
  }

  setInPoint(time = this.session.getSnapshot().currentTime): ProfessionalPlaybackSnapshot {
    const before = this.getSnapshot();
    this.inPoint = clamp(time, 0, this.session.getSnapshot().duration);
    if (this.outPoint !== null && this.outPoint <= this.inPoint) this.outPoint = null;
    return this.commitWithHistory("Set playback in point", before, "loop-changed");
  }

  setOutPoint(time = this.session.getSnapshot().currentTime): ProfessionalPlaybackSnapshot {
    const before = this.getSnapshot();
    const value = clamp(time, 0, this.session.getSnapshot().duration);
    if (this.inPoint !== null && value <= this.inPoint) {
      throw new Error("Professional playback out point must be after the in point.");
    }
    this.outPoint = value;
    return this.commitWithHistory("Set playback out point", before, "loop-changed");
  }

  setLoopMode(
    mode: ProfessionalPlaybackLoopMode,
    range: ProfessionalPlaybackRange | null = this.loopRange,
  ): ProfessionalPlaybackSnapshot {
    const before = this.getSnapshot();
    if (mode === "in-out") {
      const resolvedRange =
        range ??
        (this.inPoint !== null && this.outPoint !== null
          ? { startTime: this.inPoint, endTime: this.outPoint }
          : null);
      if (!resolvedRange || resolvedRange.endTime <= resolvedRange.startTime) {
        throw new Error("In/out loop mode requires a valid range.");
      }
      this.loopRange = { ...resolvedRange };
    } else {
      this.loopRange = range ? { ...range } : null;
    }
    this.loopMode = mode;
    this.session.setLoop(mode === "timeline");
    return this.commitWithHistory("Change playback loop mode", before, "loop-changed");
  }

  setFollowPlayhead(value: boolean): ProfessionalPlaybackSnapshot {
    this.followPlayhead = Boolean(value);
    return this.commit("advanced");
  }

  setAutoScroll(value: boolean): ProfessionalPlaybackSnapshot {
    this.autoScroll = Boolean(value);
    return this.commit("advanced");
  }

  replaceBufferedRanges(
    ranges: readonly ProfessionalPlaybackRange[],
  ): ProfessionalPlaybackSnapshot {
    this.buffer.replace(ranges, this.session.getSnapshot().currentTime);
    return this.commit("buffer-changed");
  }

  advance(nowMs: number): ProfessionalPlaybackSnapshot {
    this.assertActive();
    const deltaSeconds = this.clock.measure(nowMs);
    const state = this.session.getSnapshot();
    if (!state.playing || deltaSeconds === 0) return this.getSnapshot();

    const candidate =
      state.currentTime + deltaSeconds * state.speed * state.direction;
    const resolution = this.loop.resolve(
      candidate,
      state.duration,
      state.direction,
      this.loopMode,
      this.loopRange,
    );

    if (resolution.completed) {
      this.session.synchronizeTime(resolution.time, false);
      this.session.pause();
    } else {
      this.session.synchronizeTime(resolution.time, true);
    }

    if (resolution.looped) this.loopCount += 1;

    this.renderedFrames += 1;
    const deltaMs = deltaSeconds * 1000;
    this.averageFrameTimeMs =
      this.renderedFrames === 1
        ? deltaMs
        : (
            this.averageFrameTimeMs * (this.renderedFrames - 1) +
            deltaMs
          ) / this.renderedFrames;

    const idealFrameMs = 1000 / state.fps;
    if (deltaMs > idealFrameMs * 1.5) {
      this.droppedFrames += Math.max(1, Math.floor(deltaMs / idealFrameMs) - 1);
    }

    return this.commit(resolution.looped ? "looped" : "advanced");
  }

  setPlaybackLatency(latencyMs: number): ProfessionalPlaybackSnapshot {
    this.playbackLatencyMs = Math.max(0, latencyMs);
    return this.commit("advanced");
  }

  reset(): ProfessionalPlaybackSnapshot {
    this.session.reset();
    this.clock.reset();
    this.loopMode = "off";
    this.loopRange = null;
    this.inPoint = null;
    this.outPoint = null;
    this.loopCount = 0;
    this.renderedFrames = 0;
    this.droppedFrames = 0;
    this.averageFrameTimeMs = 0;
    this.playbackLatencyMs = 0;
    this.cache.clear();
    return this.commit("reset");
  }

  dispose(): void {
    if (this.disposed) return;
    const previous = this.getSnapshot();
    this.disposed = true;
    this.session.dispose();
    this.cache.clear();
    this.updatedAt = this.now();
    this.stateRevision += 1;
    const current = this.getSnapshot();
    const event: ProfessionalPlaybackEvent = {
      type: "disposed",
      stateRevision: current.stateRevision,
      occurredAt: current.updatedAt ?? this.now(),
    };
    for (const listener of this.listeners) {
      listener(current, previous, event);
    }
    this.listeners.clear();
  }

  private getMetrics(): ProfessionalPlaybackMetrics {
    const fps =
      this.averageFrameTimeMs > 0 ? 1000 / this.averageFrameTimeMs : 0;
    return {
      renderedFrames: this.renderedFrames,
      droppedFrames: this.droppedFrames,
      measuredFps: fps,
      averageFrameTimeMs: this.averageFrameTimeMs,
      loopCount: this.loopCount,
      playbackLatencyMs: this.playbackLatencyMs,
    };
  }

  private commit(type: ProfessionalPlaybackEventType): ProfessionalPlaybackSnapshot {
    const previous = this.getSnapshot();
    const occurredAt = this.now();
    this.stateRevision += 1;
    this.updatedAt = occurredAt;
    const current = this.getSnapshot();
    const event: ProfessionalPlaybackEvent = {
      type,
      stateRevision: current.stateRevision,
      occurredAt,
    };
    for (const listener of this.listeners) {
      listener(current, previous, event);
    }
    return current;
  }

  private commitWithHistory(
    label: string,
    before: ProfessionalPlaybackSnapshot,
    type: ProfessionalPlaybackEventType,
  ): ProfessionalPlaybackSnapshot {
    const after = this.commit(type);
    this.history?.record(label, before, after);
    return after;
  }

  private assertActive(): void {
    if (this.disposed) {
      throw new Error("Professional playback engine has been disposed.");
    }
  }
}

function mapStatus(
  state: PlaybackSessionState,
): ProfessionalPlaybackSnapshot["status"] {
  if (state.status === "disposed") return "disposed";
  if (state.status === "completed") return "completed";
  if (state.status === "playing") return "playing";
  if (state.status === "paused" || state.status === "seeking") return "paused";
  if (state.status === "ready") return "ready";
  return "idle";
}

function clamp(value: number, minimum: number, maximum: number): number {
  if (!Number.isFinite(value)) throw new Error("Playback value must be finite.");
  return Math.min(maximum, Math.max(minimum, value));
}
