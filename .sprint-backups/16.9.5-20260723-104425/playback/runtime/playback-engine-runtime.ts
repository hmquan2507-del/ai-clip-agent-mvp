import type {
  PlaybackConfiguration,
  PlaybackDirection,
  PlaybackEvent,
  PlaybackHistoryPort,
  PlaybackMediaPort,
  PlaybackMetrics,
  PlaybackSnapshot,
  PlaybackStatus,
} from "../contracts/professional-playback-contracts";
import { PlaybackClockRuntime } from "./playback-clock-runtime";
import { PlaybackLoopRuntime } from "./playback-loop-runtime";
import { PlaybackSpeedRuntime } from "./playback-speed-runtime";

type Listener = (event: PlaybackEvent) => void;

export class PlaybackEngineRuntime {
  private status: PlaybackStatus = "idle";
  private currentTimeSeconds: number;
  private inPointSeconds: number | null = null;
  private outPointSeconds: number | null = null;
  private followPlayhead: boolean;
  private autoScroll: boolean;
  private listeners = new Set<Listener>();
  private metrics: PlaybackMetrics = {
    renderedFrames: 0,
    droppedFrames: 0,
    measuredFps: 0,
    averageFrameTimeMs: 0,
    playbackLatencyMs: 0,
    audioVideoDriftSeconds: 0,
  };

  readonly clock = new PlaybackClockRuntime();
  readonly speed: PlaybackSpeedRuntime;
  readonly loop = new PlaybackLoopRuntime();

  constructor(
    private readonly config: PlaybackConfiguration,
    private readonly media?: PlaybackMediaPort,
    private readonly history?: PlaybackHistoryPort,
  ) {
    if (!Number.isFinite(config.durationSeconds) || config.durationSeconds <= 0) {
      throw new Error("Playback duration must be greater than zero.");
    }
    if (!Number.isFinite(config.frameRate) || config.frameRate <= 0) {
      throw new Error("Playback frame rate must be greater than zero.");
    }
    this.currentTimeSeconds = this.clamp(config.initialTimeSeconds ?? 0);
    this.followPlayhead = config.followPlayhead ?? true;
    this.autoScroll = config.autoScroll ?? true;
    this.speed = new PlaybackSpeedRuntime(config.initialSpeed ?? 1, config.minSpeed ?? 0.25, config.maxSpeed ?? 8);
    this.loop.setMode(config.loopMode ?? "off", config.loopRange ?? null);
  }

  subscribe(listener: Listener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  snapshot(): PlaybackSnapshot {
    return {
      status: this.status,
      currentTimeSeconds: this.currentTimeSeconds,
      durationSeconds: this.config.durationSeconds,
      speed: this.speed.getSpeed(),
      direction: this.speed.getDirection(),
      loopMode: this.loop.getMode(),
      loopRange: this.loop.getRange(),
      inPointSeconds: this.inPointSeconds,
      outPointSeconds: this.outPointSeconds,
      followPlayhead: this.followPlayhead,
      autoScroll: this.autoScroll,
    };
  }

  restore(snapshot: PlaybackSnapshot, recordHistory = false): void {
    const before = this.snapshot();
    this.status = snapshot.status;
    this.currentTimeSeconds = this.clamp(snapshot.currentTimeSeconds);
    this.speed.setSpeed(snapshot.speed);
    this.speed.setDirection(snapshot.direction);
    this.loop.setMode(snapshot.loopMode, snapshot.loopRange);
    this.inPointSeconds = snapshot.inPointSeconds;
    this.outPointSeconds = snapshot.outPointSeconds;
    this.followPlayhead = snapshot.followPlayhead;
    this.autoScroll = snapshot.autoScroll;
    this.media?.seek(this.currentTimeSeconds);
    this.media?.setRate(this.signedRate());
    const after = this.snapshot();
    if (recordHistory) this.history?.record("Restore playback snapshot", before, after);
    this.emit({ type: "snapshot-restored", snapshot: after });
  }

  async play(): Promise<void> {
    if (this.status === "ended") this.seek(this.speed.getDirection() === "forward" ? 0 : this.config.durationSeconds);
    this.setStatus("playing");
    this.clock.reset();
    this.media?.setRate(this.signedRate());
    await this.media?.play();
  }

  pause(): void {
    this.media?.pause();
    this.setStatus("paused");
  }

  stop(): void {
    this.media?.pause();
    this.seek(this.speed.getDirection() === "forward" ? 0 : this.config.durationSeconds);
    this.setStatus("stopped");
  }

  togglePlayPause(): Promise<void> | void {
    if (this.status === "playing") return this.pause();
    return this.play();
  }

  seek(timeSeconds: number): number {
    this.currentTimeSeconds = this.snapToFrame(this.clamp(timeSeconds));
    this.media?.seek(this.currentTimeSeconds);
    this.emitTime();
    return this.currentTimeSeconds;
  }

  stepFrames(frameDelta: number): number {
    if (!Number.isInteger(frameDelta)) throw new Error("Frame delta must be an integer.");
    this.pause();
    return this.seek(this.currentTimeSeconds + frameDelta / this.config.frameRate);
  }

  stepForward(): number { return this.stepFrames(1); }
  stepBackward(): number { return this.stepFrames(-1); }

  jumpToStart(): number { return this.seek(0); }
  jumpToEnd(): number { return this.seek(this.config.durationSeconds); }

  setSpeed(speed: number): number {
    const value = this.speed.setSpeed(speed);
    this.media?.setRate(this.signedRate());
    this.emit({ type: "speed-changed", speed: value });
    return value;
  }

  setDirection(direction: PlaybackDirection): PlaybackDirection {
    const value = this.speed.setDirection(direction);
    this.media?.setRate(this.signedRate());
    this.emit({ type: "direction-changed", direction: value });
    return value;
  }

  j(): number {
    this.setDirection("reverse");
    const value = this.speed.shuttleReverse();
    this.media?.setRate(this.signedRate());
    this.emit({ type: "speed-changed", speed: value });
    void this.play();
    return value;
  }

  k(): void {
    this.pause();
    this.speed.pauseShuttle();
    this.emit({ type: "speed-changed", speed: this.speed.getSpeed() });
  }

  l(): number {
    this.setDirection("forward");
    const value = this.speed.shuttleForward();
    this.media?.setRate(this.signedRate());
    this.emit({ type: "speed-changed", speed: value });
    void this.play();
    return value;
  }

  setInPoint(timeSeconds = this.currentTimeSeconds): number {
    const before = this.snapshot();
    this.inPointSeconds = this.snapToFrame(this.clamp(timeSeconds));
    if (this.outPointSeconds !== null && this.outPointSeconds <= this.inPointSeconds) this.outPointSeconds = null;
    this.record("Set playback in point", before);
    return this.inPointSeconds;
  }

  setOutPoint(timeSeconds = this.currentTimeSeconds): number {
    const before = this.snapshot();
    const value = this.snapToFrame(this.clamp(timeSeconds));
    if (this.inPointSeconds !== null && value <= this.inPointSeconds) throw new Error("Out point must be after in point.");
    this.outPointSeconds = value;
    this.record("Set playback out point", before);
    return value;
  }

  enableInOutLoop(): void {
    if (this.inPointSeconds === null || this.outPointSeconds === null) throw new Error("Set in and out points before enabling in/out loop.");
    this.loop.setMode("in-out", { startSeconds: this.inPointSeconds, endSeconds: this.outPointSeconds });
  }

  setFollowPlayhead(enabled: boolean): void { this.followPlayhead = enabled; }
  setAutoScroll(enabled: boolean): void { this.autoScroll = enabled; }

  advance(nowMs: number): PlaybackSnapshot {
    if (this.status !== "playing") return this.snapshot();
    const tick = this.clock.tick(
      nowMs,
      this.currentTimeSeconds,
      this.speed.getSpeed(),
      this.speed.getDirection(),
      this.config.frameRate,
    );
    const resolution = this.loop.resolve(tick.currentTimeSeconds, this.config.durationSeconds, this.speed.getDirection());
    this.currentTimeSeconds = this.snapToFrame(this.clamp(resolution.timeSeconds));
    if (resolution.looped) this.emit({ type: "looped", timeSeconds: this.currentTimeSeconds, loopCount: this.loop.getLoopCount() });
    if (resolution.ended) {
      this.media?.pause();
      this.setStatus("ended");
    }
    this.metrics.renderedFrames += 1;
    this.metrics.averageFrameTimeMs =
      this.metrics.renderedFrames === 1
        ? tick.deltaMs
        : ((this.metrics.averageFrameTimeMs * (this.metrics.renderedFrames - 1)) + tick.deltaMs) / this.metrics.renderedFrames;
    this.metrics.measuredFps = tick.deltaMs > 0 ? 1000 / tick.deltaMs : this.metrics.measuredFps;
    const idealFrameMs = 1000 / this.config.frameRate;
    if (tick.deltaMs > idealFrameMs * 1.5) this.metrics.droppedFrames += Math.max(1, Math.floor(tick.deltaMs / idealFrameMs) - 1);
    this.emitTime();
    this.emit({ type: "metrics-changed", metrics: this.getMetrics() });
    return this.snapshot();
  }

  getMetrics(): PlaybackMetrics { return { ...this.metrics }; }

  updateLatency(latencyMs: number): void {
    this.metrics.playbackLatencyMs = Math.max(0, latencyMs);
  }

  updateAudioVideoDrift(driftSeconds: number): void {
    this.metrics.audioVideoDriftSeconds = driftSeconds;
  }

  private signedRate(): number {
    return this.speed.getSpeed() * (this.speed.getDirection() === "forward" ? 1 : -1);
  }

  private snapToFrame(timeSeconds: number): number {
    return Math.round(timeSeconds * this.config.frameRate) / this.config.frameRate;
  }

  private clamp(timeSeconds: number): number {
    if (!Number.isFinite(timeSeconds)) throw new Error("Playback time must be finite.");
    return Math.min(this.config.durationSeconds, Math.max(0, timeSeconds));
  }

  private setStatus(status: PlaybackStatus): void {
    if (this.status === status) return;
    this.status = status;
    this.emit({ type: "status-changed", status });
  }

  private emitTime(): void {
    this.emit({
      type: "time-changed",
      timeSeconds: this.currentTimeSeconds,
      frame: Math.round(this.currentTimeSeconds * this.config.frameRate),
    });
  }

  private record(label: string, before: PlaybackSnapshot): void {
    this.history?.record(label, before, this.snapshot());
  }

  private emit(event: PlaybackEvent): void {
    for (const listener of this.listeners) listener(event);
  }
}
