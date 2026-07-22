import {
  VIDEO_PREVIEW_CONTRACT_VERSION,
  type VideoPreviewConfiguration,
  type VideoPreviewEvent,
  type VideoPreviewEventType,
  type VideoPreviewListener,
  type VideoPreviewPort,
  type VideoPreviewSnapshot,
  type VideoPreviewSyncSource,
} from "../contracts";
import type { PlaybackSessionRuntime } from "./playback-session-runtime";
import type { PlayheadRuntime } from "./playhead-runtime";
import { assertPositiveNumber, clampPlaybackTime } from "./playback-time-model";

export interface VideoPreviewSynchronizerOptions {
  now?: () => string;
}

export class VideoPreviewSynchronizer {
  private state: VideoPreviewSnapshot;
  private readonly listeners = new Set<VideoPreviewListener>();
  private readonly unsubscribeMedia: Array<() => void> = [];
  private readonly now: () => string;
  private readonly fps: number;
  private readonly driftThreshold: number;
  private readonly largeDriftThreshold: number;
  private port: VideoPreviewPort | null = null;
  private suppressMediaSeek = false;
  private disposed = false;

  constructor(
    private readonly playback: PlaybackSessionRuntime,
    private readonly playhead: PlayheadRuntime,
    configuration: VideoPreviewConfiguration,
    options: VideoPreviewSynchronizerOptions = {},
  ) {
    this.fps = assertPositiveNumber(configuration.fps, "fps");
    this.driftThreshold = Math.max(configuration.driftThreshold ?? 0, 1 / this.fps, 0.04);
    this.largeDriftThreshold = Math.max(configuration.largeDriftThreshold ?? 0.5, this.driftThreshold);
    this.now = options.now ?? (() => new Date().toISOString());
    this.state = {
      contractVersion: VIDEO_PREVIEW_CONTRACT_VERSION,
      status: "detached",
      attached: false,
      currentTimeSeconds: 0,
      durationSeconds: 0,
      playbackRate: 1,
      paused: true,
      seeking: false,
      buffering: false,
      ended: false,
      driftSeconds: 0,
      lastSource: null,
      errorMessage: null,
      stateRevision: 0,
      updatedAt: null,
    };
  }

  getSnapshot(): VideoPreviewSnapshot { return { ...this.state }; }
  getState(): VideoPreviewSnapshot { return this.getSnapshot(); }

  subscribe(listener: VideoPreviewListener): () => void {
    this.assertActive();
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  attach(port: VideoPreviewPort): VideoPreviewSnapshot {
    this.assertActive();
    if (this.port === port) return this.getSnapshot();
    this.detach();
    this.port = port;
    for (const event of ["loadedmetadata", "timeupdate", "seeking", "seeked", "ended", "waiting", "playing", "pause", "error"] as const) {
      this.unsubscribeMedia.push(port.subscribe(event, () => this.handleMediaEvent(event)));
    }
    return this.commit(this.readPortState("loading", "media-event"), "attached");
  }

  detach(): VideoPreviewSnapshot {
    this.assertActive();
    while (this.unsubscribeMedia.length) this.unsubscribeMedia.pop()?.();
    this.port = null;
    this.suppressMediaSeek = false;
    if (!this.state.attached && this.state.status === "detached") return this.getSnapshot();
    return this.commit({ ...this.state, status: "detached", attached: false, buffering: false, seeking: false, lastSource: null }, "detached");
  }

  async syncFromPlayback(): Promise<VideoPreviewSnapshot> {
    this.assertActive();
    const port = this.requirePort();
    const playback = this.playback.getSnapshot();
    if (Math.abs(port.playbackRate - playback.speed) > Number.EPSILON) {
      port.setPlaybackRate(playback.speed);
    }
    const drift = port.currentTime - playback.currentTime;
    if (Math.abs(drift) > this.driftThreshold) this.setMediaTime(playback.currentTime, "playback-command");
    if (playback.playing && port.paused) {
      try { await port.play(); }
      catch (error) { return this.fail(error); }
    } else if (!playback.playing && !port.paused) {
      port.pause();
    }
    return this.commit(this.readPortState(playback.playing ? "playing" : "paused", "playback-command", drift), playback.playing ? "play-synced" : "pause-synced");
  }

  async play(): Promise<VideoPreviewSnapshot> {
    this.assertActive();
    const port = this.requirePort();
    this.playback.play();
    if (!port.paused) return this.getSnapshot();
    try { await port.play(); }
    catch (error) { return this.fail(error); }
    return this.commit(this.readPortState("playing", "playback-command"), "play-synced");
  }

  pause(): VideoPreviewSnapshot {
    this.assertActive();
    const port = this.requirePort();
    this.playback.pause();
    if (!port.paused) port.pause();
    return this.commit(this.readPortState("paused", "playback-command"), "pause-synced");
  }

  stop(): VideoPreviewSnapshot {
    this.assertActive();
    const port = this.requirePort();
    const playback = this.playback.stop();
    if (!port.paused) port.pause();
    this.setMediaTime(playback.currentTime, "playback-command");
    this.playhead.syncFromPlayback(playback);
    return this.commit(this.readPortState("paused", "playback-command"), "stop-synced");
  }

  seek(time: number, source: VideoPreviewSyncSource = "playback-command"): VideoPreviewSnapshot {
    this.assertActive();
    const target = clampPlaybackTime(time, this.playback.getSnapshot().duration);
    const playback = this.playback.seek(target);
    this.setMediaTime(target, source);
    this.playhead.syncFromPlayback(playback);
    return this.commit(this.readPortState("seeking", source), "seek-synced");
  }

  setPlaybackRate(rate: number): VideoPreviewSnapshot {
    this.assertActive();
    assertPositiveNumber(rate, "rate");
    const port = this.requirePort();
    this.playback.setSpeed(rate);
    if (Math.abs(port.playbackRate - rate) > Number.EPSILON) port.setPlaybackRate(rate);
    return this.commit(this.readPortState(this.state.status, "playback-command"), "rate-synced");
  }

  syncFromMedia(): VideoPreviewSnapshot {
    this.assertActive();
    const port = this.requirePort();
    if (this.playhead.getSnapshot().isDragging) return this.getSnapshot();
    const playback = this.playback.synchronizeTime(port.currentTime, !port.paused && !port.ended);
    this.playhead.syncFromPlayback(playback);
    return this.commit(this.readPortState(port.ended ? "ended" : port.paused ? "paused" : "playing", "media-event"), port.ended ? "media-ended" : "media-time-synced");
  }

  reset(): VideoPreviewSnapshot {
    this.assertActive();
    if (this.port) {
      if (!this.port.paused) this.port.pause();
      this.setMediaTime(0, "internal-correction");
      if (Math.abs(this.port.playbackRate - 1) > Number.EPSILON) this.port.setPlaybackRate(1);
    }
    this.playback.reset();
    this.playhead.reset();
    return this.commit({ ...this.state, status: this.port ? "ready" : "detached", attached: Boolean(this.port), currentTimeSeconds: 0, playbackRate: 1, paused: true, seeking: false, buffering: false, ended: false, driftSeconds: 0, errorMessage: null, lastSource: "internal-correction" }, "reset");
  }

  dispose(): void {
    if (this.disposed) return;
    while (this.unsubscribeMedia.length) this.unsubscribeMedia.pop()?.();
    this.port = null;
    this.listeners.clear();
    this.disposed = true;
    this.state = { ...this.state, status: "disposed", attached: false, buffering: false, seeking: false, updatedAt: this.now() };
  }

  private handleMediaEvent(event: string): void {
    if (!this.port || this.disposed) return;
    if (event === "loadedmetadata") {
      this.commit(this.readPortState("ready", "media-event"), "metadata-synced");
      return;
    }
    if (event === "waiting") {
      this.commit({ ...this.readPortState("buffering", "media-event"), buffering: true }, "buffering-started");
      return;
    }
    if (event === "playing") {
      this.commit({ ...this.readPortState("playing", "media-event"), buffering: false }, "buffering-ended");
      return;
    }
    if (event === "seeking") {
      this.commit(this.readPortState("seeking", "media-event"), "seek-synced");
      return;
    }
    if (event === "seeked" && this.suppressMediaSeek) {
      this.suppressMediaSeek = false;
      this.commit(this.readPortState(this.port.paused ? "paused" : "playing", "internal-correction"), "seek-synced");
      return;
    }
    if (event === "timeupdate" || event === "seeked" || event === "ended" || event === "pause") {
      this.syncFromMedia();
      return;
    }
    if (event === "error") this.fail(new Error("Video preview media error."));
  }

  private setMediaTime(time: number, source: VideoPreviewSyncSource): void {
    const port = this.requirePort();
    const bounded = clampPlaybackTime(time, Number.isFinite(port.duration) ? port.duration : this.playback.getSnapshot().duration);
    if (Math.abs(port.currentTime - bounded) <= this.driftThreshold) return;
    this.suppressMediaSeek = true;
    port.setCurrentTime(bounded);
    this.state = { ...this.state, lastSource: source };
  }

  private readPortState(status: VideoPreviewSnapshot["status"], source: VideoPreviewSyncSource, drift?: number): VideoPreviewSnapshot {
    const port = this.requirePort();
    const duration = Number.isFinite(port.duration) && port.duration >= 0 ? port.duration : 0;
    return { ...this.state, status, attached: true, currentTimeSeconds: Number.isFinite(port.currentTime) ? Math.max(0, port.currentTime) : 0, durationSeconds: duration, playbackRate: Number.isFinite(port.playbackRate) && port.playbackRate > 0 ? port.playbackRate : 1, paused: port.paused, seeking: port.seeking, buffering: status === "buffering" ? true : this.state.buffering, ended: port.ended, driftSeconds: drift ?? port.currentTime - this.playback.getSnapshot().currentTime, lastSource: source, errorMessage: null };
  }

  private fail(error: unknown): VideoPreviewSnapshot {
    const message = error instanceof Error ? error.message : String(error);
    return this.commit({ ...this.state, status: "error", errorMessage: message, buffering: false }, "error");
  }

  private commit(candidate: VideoPreviewSnapshot, eventType: VideoPreviewEventType): VideoPreviewSnapshot {
    const previous = { ...this.state };
    const occurredAt = this.now();
    this.state = { ...candidate, stateRevision: this.state.stateRevision + 1, updatedAt: occurredAt };
    const current = { ...this.state };
    const event: VideoPreviewEvent = { type: eventType, stateRevision: current.stateRevision, occurredAt };
    for (const listener of this.listeners) listener({ ...current }, { ...previous }, { ...event });
    return current;
  }

  private requirePort(): VideoPreviewPort {
    if (!this.port) throw new Error("Video preview is not attached.");
    return this.port;
  }

  private assertActive(): void {
    if (this.disposed) throw new Error("Video preview synchronizer has been disposed.");
  }
}

export function createVideoPreviewSynchronizer(
  playback: PlaybackSessionRuntime,
  playhead: PlayheadRuntime,
  configuration: VideoPreviewConfiguration,
  options: VideoPreviewSynchronizerOptions = {},
): VideoPreviewSynchronizer {
  return new VideoPreviewSynchronizer(playback, playhead, configuration, options);
}
