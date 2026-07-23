import type {
  PlaybackBufferSnapshot,
  PlaybackConfiguration,
  PlaybackEvent,
  PlaybackHistoryPort,
  PlaybackMediaPort,
  PlaybackSchedulerPort,
  PlaybackSnapshot,
  PlaybackSyncSnapshot,
  PlaybackViewportPort,
} from "../contracts/professional-playback-contracts";
import { PlaybackBufferRuntime } from "./playback-buffer-runtime";
import { PlaybackCacheRuntime } from "./playback-cache-runtime";
import { PlaybackEngineRuntime } from "./playback-engine-runtime";
import { PlaybackSyncRuntime } from "./playback-sync-runtime";

export class TimelineProfessionalPlaybackRuntime {
  readonly engine: PlaybackEngineRuntime;
  readonly cache: PlaybackCacheRuntime;
  readonly buffer: PlaybackBufferRuntime;
  readonly sync: PlaybackSyncRuntime;

  private schedulerHandle: number | null = null;
  private readonly scheduler?: PlaybackSchedulerPort;

  constructor(
    config: PlaybackConfiguration,
    ports: {
      media?: PlaybackMediaPort;
      history?: PlaybackHistoryPort;
      viewport?: PlaybackViewportPort;
      scheduler?: PlaybackSchedulerPort;
    } = {},
  ) {
    this.engine = new PlaybackEngineRuntime(config, ports.media, ports.history);
    this.cache = new PlaybackCacheRuntime(config.cacheCapacity ?? 240);
    this.buffer = new PlaybackBufferRuntime(config.bufferTargetSeconds ?? 6, config.lowBufferThresholdSeconds ?? 1.5);
    this.sync = new PlaybackSyncRuntime(config.syncThresholdSeconds ?? 0.08, ports.viewport);
    this.scheduler = ports.scheduler;

    this.engine.subscribe((event) => {
      if (event.type === "status-changed") {
        if (event.status === "playing") this.startScheduler();
        else this.stopScheduler();
      }
      if (event.type === "time-changed") {
        const state = this.engine.snapshot();
        this.sync.synchronize(event.timeSeconds, state.followPlayhead, state.autoScroll);
      }
    });
  }

  subscribe(listener: (event: PlaybackEvent) => void): () => void {
    return this.engine.subscribe(listener);
  }

  snapshot(): PlaybackSnapshot { return this.engine.snapshot(); }
  restore(snapshot: PlaybackSnapshot, recordHistory = false): void { this.engine.restore(snapshot, recordHistory); }

  updateBufferedRanges(ranges: Array<{ startSeconds: number; endSeconds: number }>): PlaybackBufferSnapshot {
    return this.buffer.replace(ranges);
  }

  getBufferSnapshot(): PlaybackBufferSnapshot {
    return this.buffer.snapshot(this.engine.snapshot().currentTimeSeconds);
  }

  synchronizeMedia(audioSeconds: number, videoSeconds: number): PlaybackSyncSnapshot {
    this.sync.updateMediaTimes(audioSeconds, videoSeconds);
    const state = this.engine.snapshot();
    const result = this.sync.synchronize(state.currentTimeSeconds, state.followPlayhead, state.autoScroll);
    this.engine.updateAudioVideoDrift(result.driftSeconds);
    return result;
  }

  handleKeyboardKey(key: string): boolean {
    switch (key.toLowerCase()) {
      case "j":
        this.engine.j();
        return true;
      case "k":
        this.engine.k();
        return true;
      case "l":
        this.engine.l();
        return true;
      case "arrowleft":
        this.engine.stepBackward();
        return true;
      case "arrowright":
        this.engine.stepForward();
        return true;
      case " ":
      case "space":
        void this.engine.togglePlayPause();
        return true;
      default:
        return false;
    }
  }

  dispose(): void {
    this.stopScheduler();
    this.engine.pause();
    this.cache.clear();
  }

  private startScheduler(): void {
    if (!this.scheduler || this.schedulerHandle !== null) return;
    const loop = (nowMs: number) => {
      this.engine.advance(nowMs);
      if (this.engine.snapshot().status === "playing") {
        this.schedulerHandle = this.scheduler!.request(loop);
      } else {
        this.schedulerHandle = null;
      }
    };
    this.schedulerHandle = this.scheduler.request(loop);
  }

  private stopScheduler(): void {
    if (!this.scheduler || this.schedulerHandle === null) return;
    this.scheduler.cancel(this.schedulerHandle);
    this.schedulerHandle = null;
  }
}
