import type {
  AudioSynchronizationSnapshot,
  ProfessionalPlaybackConfiguration,
  ProfessionalPlaybackEvent,
  ProfessionalPlaybackPorts,
  ProfessionalPlaybackSnapshot,
  VideoPreviewSnapshot,
} from "../contracts";
import { AudioSynchronizationRuntime } from "./audio-synchronization-runtime";
import { PlaybackEngineRuntime } from "./playback-engine-runtime";
import { PlaybackSyncRuntime } from "./playback-sync-runtime";
import { PlayheadRuntime } from "./playhead-runtime";
import { VideoPreviewSynchronizer } from "./video-preview-synchronizer";

export interface TimelineProfessionalPlaybackSnapshot {
  readonly playback: ProfessionalPlaybackSnapshot;
  readonly video: VideoPreviewSnapshot | null;
  readonly audio: AudioSynchronizationSnapshot | null;
}

export class TimelineProfessionalPlaybackRuntime {
  readonly engine: PlaybackEngineRuntime;
  readonly playhead: PlayheadRuntime;
  readonly video: VideoPreviewSynchronizer;
  readonly audio: AudioSynchronizationRuntime;
  readonly sync: PlaybackSyncRuntime;

  private schedulerHandle: number | null = null;
  private readonly scheduler: ProfessionalPlaybackPorts["scheduler"];
  private readonly unsubscribeEngine: () => void;
  private disposed = false;

  constructor(
    configuration: ProfessionalPlaybackConfiguration,
    ports: ProfessionalPlaybackPorts = {},
  ) {
    this.engine = new PlaybackEngineRuntime(configuration, {
      now: ports.now,
      history: ports.history,
    });

    this.playhead = new PlayheadRuntime(
      {
        duration: configuration.duration,
        fps: configuration.fps,
        initialTime: configuration.initialTime,
        pixelsPerSecond: configuration.pixelsPerSecond,
        viewportWidth: configuration.viewportWidth,
        scrollOffset: configuration.scrollOffset,
      },
      {
        now: ports.now,
        requestSeek: (time) => {
          this.seek(time);
        },
      },
    );

    this.video = new VideoPreviewSynchronizer(
      this.engine.session,
      this.playhead,
      { fps: configuration.fps },
      { now: ports.now },
    );

    this.audio = new AudioSynchronizationRuntime(
      this.engine.session,
      { fps: configuration.fps },
      { now: ports.now },
    );

    this.sync = new PlaybackSyncRuntime(this.playhead, ports.viewport);
    this.scheduler = ports.scheduler;

    if (ports.video) this.video.attach(ports.video);
    for (const track of ports.audio ?? []) {
      this.audio.attachTrack(track.descriptor, track.port);
    }

    this.unsubscribeEngine = this.engine.subscribe((state, _previous, event) => {
      this.sync.synchronize(
        state.session,
        state.followPlayhead,
        state.autoScroll,
      );
      this.handleEngineEvent(event);
    });
  }

  subscribe(
    listener: (
      state: ProfessionalPlaybackSnapshot,
      previous: ProfessionalPlaybackSnapshot,
      event: ProfessionalPlaybackEvent,
    ) => void,
  ): () => void {
    return this.engine.subscribe(listener);
  }

  getSnapshot(): TimelineProfessionalPlaybackSnapshot {
    return {
      playback: this.engine.getSnapshot(),
      video: this.video.getSnapshot(),
      audio: this.audio.getSnapshot(),
    };
  }

  ready(): TimelineProfessionalPlaybackSnapshot {
    this.playhead.ready();
    this.engine.ready();
    return this.getSnapshot();
  }

  async play(): Promise<TimelineProfessionalPlaybackSnapshot> {
    this.engine.play();
    await this.syncMedia();
    this.startScheduler();
    return this.getSnapshot();
  }

  pause(): TimelineProfessionalPlaybackSnapshot {
    this.stopScheduler();
    this.engine.pause();
    this.video.getSnapshot().attached && this.video.pause();
    this.audio.pause();
    return this.getSnapshot();
  }

  stop(): TimelineProfessionalPlaybackSnapshot {
    this.stopScheduler();
    this.engine.stop();
    if (this.video.getSnapshot().attached) this.video.stop();
    this.audio.stop();
    return this.getSnapshot();
  }

  async togglePlayPause(): Promise<TimelineProfessionalPlaybackSnapshot> {
    return this.engine.getSnapshot().session.playing ? this.pause() : this.play();
  }

  seek(time: number): TimelineProfessionalPlaybackSnapshot {
    this.engine.seek(time);
    if (this.video.getSnapshot().attached) this.video.seek(time);
    this.audio.seek(time);
    this.playhead.syncFromPlayback(this.engine.getSnapshot().session);
    return this.getSnapshot();
  }

  stepForward(frames = 1): TimelineProfessionalPlaybackSnapshot {
    this.engine.stepForward(frames);
    return this.seek(this.engine.getSnapshot().session.currentTime);
  }

  stepBackward(frames = 1): TimelineProfessionalPlaybackSnapshot {
    this.engine.stepBackward(frames);
    return this.seek(this.engine.getSnapshot().session.currentTime);
  }

  setSpeed(speed: number): TimelineProfessionalPlaybackSnapshot {
    this.engine.setSpeed(speed);
    if (this.video.getSnapshot().attached) this.video.setPlaybackRate(speed);
    this.audio.setPlaybackRate(speed);
    return this.getSnapshot();
  }

  async j(): Promise<TimelineProfessionalPlaybackSnapshot> {
    this.engine.j();
    await this.syncMedia();
    this.startScheduler();
    return this.getSnapshot();
  }

  k(): TimelineProfessionalPlaybackSnapshot {
    this.engine.k();
    return this.pause();
  }

  async l(): Promise<TimelineProfessionalPlaybackSnapshot> {
    this.engine.l();
    await this.syncMedia();
    this.startScheduler();
    return this.getSnapshot();
  }

  handleKeyboardKey(key: string): boolean {
    switch (key.toLowerCase()) {
      case "j":
        void this.j();
        return true;
      case "k":
        this.k();
        return true;
      case "l":
        void this.l();
        return true;
      case "arrowleft":
        this.stepBackward();
        return true;
      case "arrowright":
        this.stepForward();
        return true;
      case " ":
      case "space":
        void this.togglePlayPause();
        return true;
      default:
        return false;
    }
  }

  replaceBufferedRanges(
    ranges: ReadonlyArray<{ startTime: number; endTime: number }>,
  ): TimelineProfessionalPlaybackSnapshot {
    this.engine.replaceBufferedRanges(ranges);
    return this.getSnapshot();
  }

  reset(): TimelineProfessionalPlaybackSnapshot {
    this.stopScheduler();
    this.engine.reset();
    this.video.reset();
    this.audio.reset();
    this.playhead.reset();
    return this.getSnapshot();
  }

  dispose(): void {
    if (this.disposed) return;
    this.stopScheduler();
    this.unsubscribeEngine();
    this.video.dispose();
    this.audio.dispose();
    this.playhead.dispose();
    this.engine.dispose();
    this.disposed = true;
  }

  private async syncMedia(): Promise<void> {
    if (this.video.getSnapshot().attached) {
      await this.video.syncFromPlayback();
    }
    await this.audio.syncFromPlayback();
  }

  private handleEngineEvent(event: ProfessionalPlaybackEvent): void {
    if (event.type === "paused" || event.type === "stopped") {
      this.stopScheduler();
    }
    if (event.type === "advanced" || event.type === "looped") {
      void this.syncMedia();
    }
  }

  private startScheduler(): void {
    if (!this.scheduler || this.schedulerHandle !== null) return;
    const tick = (nowMs: number) => {
      this.engine.advance(nowMs);
      if (this.engine.getSnapshot().session.playing) {
        this.schedulerHandle = this.scheduler!.request(tick);
      } else {
        this.schedulerHandle = null;
      }
    };
    this.schedulerHandle = this.scheduler.request(tick);
  }

  private stopScheduler(): void {
    if (!this.scheduler || this.schedulerHandle === null) return;
    this.scheduler.cancel(this.schedulerHandle);
    this.schedulerHandle = null;
  }
}
