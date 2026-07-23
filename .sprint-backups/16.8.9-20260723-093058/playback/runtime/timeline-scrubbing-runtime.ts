import {
  TIMELINE_SCRUBBING_CONTRACT_VERSION,
  type AudioScrubbingPolicy,
  type ScrubbingAudioPort,
  type ScrubbingPlaybackPort,
  type ScrubbingPlayheadPort,
  type ScrubbingVideoPort,
  type TimelineScrubbingConfiguration,
  type TimelineScrubbingEvent,
  type TimelineScrubbingEventType,
  type TimelineScrubbingListener,
  type TimelineScrubbingSnapshot,
} from "../contracts";
import { shouldEmitScrubPreview, type ScrubbingThrottleState } from "./scrubbing-throttle-model";

export interface TimelineScrubbingRuntimeOptions { now?: () => string; nowMs?: () => number; }

export class TimelineScrubbingRuntime {
  private state: TimelineScrubbingSnapshot;
  private readonly listeners = new Set<TimelineScrubbingListener>();
  private readonly now: () => string;
  private readonly nowMs: () => number;
  private throttle: ScrubbingThrottleState = { lastPreviewAtMs: null, lastPreviewTimeSeconds: null };
  private disposed = false;
  private durationSeconds: number;
  private fps: number;
  private snapToFrames: boolean;
  private previewIntervalMs: number;
  private minimumDeltaSeconds: number;
  private audioPolicy: AudioScrubbingPolicy;
  private restoreMasterMuted: boolean | null = null;

  constructor(
    private readonly playback: ScrubbingPlaybackPort,
    private readonly playhead: ScrubbingPlayheadPort,
    private readonly video: ScrubbingVideoPort,
    private readonly audio: ScrubbingAudioPort,
    configuration: TimelineScrubbingConfiguration,
    options: TimelineScrubbingRuntimeOptions = {},
  ) {
    this.durationSeconds = finiteNonNegative(configuration.durationSeconds, "durationSeconds");
    this.fps = finitePositive(configuration.fps, "fps");
    this.snapToFrames = configuration.snapToFrames ?? true;
    this.previewIntervalMs = Math.max(0, configuration.previewIntervalMs ?? 16);
    this.minimumDeltaSeconds = Math.max(configuration.minimumPreviewDeltaSeconds ?? Math.max(1 / this.fps, .02), 0);
    this.audioPolicy = configuration.audioPolicy ?? "muted";
    this.now = options.now ?? (() => new Date().toISOString());
    this.nowMs = options.nowMs ?? (() => Date.now());
    const initial = clamp(this.playback.getSnapshot().currentTime, 0, this.durationSeconds);
    this.state = {
      contractVersion: TIMELINE_SCRUBBING_CONTRACT_VERSION,
      status: "idle",
      previewTimeSeconds: initial,
      committedTimeSeconds: initial,
      originTimeSeconds: initial,
      wasPlayingBeforeScrub: false,
      resumePlaybackOnCommit: configuration.resumePlaybackOnCommit ?? true,
      previewFrame: toFrame(initial, this.fps),
      pointerPixel: null,
      audioPolicy: this.audioPolicy,
      stateRevision: 0,
      updatedAt: null,
    };
  }

  getSnapshot(): TimelineScrubbingSnapshot { return { ...this.state }; }
  getState(): TimelineScrubbingSnapshot { return this.getSnapshot(); }
  subscribe(listener: TimelineScrubbingListener): () => void { this.assertActive(); this.listeners.add(listener); return () => this.listeners.delete(listener); }
  ready(): TimelineScrubbingSnapshot { this.assertActive(); return this.commit({ ...this.state, status: "ready" }, "ready"); }

  configure(configuration: Partial<TimelineScrubbingConfiguration>): TimelineScrubbingSnapshot {
    this.assertActive();
    if (configuration.durationSeconds !== undefined) this.durationSeconds = finiteNonNegative(configuration.durationSeconds, "durationSeconds");
    if (configuration.fps !== undefined) this.fps = finitePositive(configuration.fps, "fps");
    if (configuration.snapToFrames !== undefined) this.snapToFrames = Boolean(configuration.snapToFrames);
    if (configuration.previewIntervalMs !== undefined) this.previewIntervalMs = Math.max(0, configuration.previewIntervalMs);
    if (configuration.minimumPreviewDeltaSeconds !== undefined) this.minimumDeltaSeconds = Math.max(0, configuration.minimumPreviewDeltaSeconds);
    if (configuration.audioPolicy !== undefined) this.audioPolicy = configuration.audioPolicy;
    if (configuration.resumePlaybackOnCommit !== undefined) this.state = { ...this.state, resumePlaybackOnCommit: Boolean(configuration.resumePlaybackOnCommit) };
    return this.commit({ ...this.state, audioPolicy: this.audioPolicy }, "configured");
  }

  beginScrub(): TimelineScrubbingSnapshot {
    this.assertActive();
    if (this.state.status === "scrubbing") return this.getSnapshot();
    const playback = this.playback.getSnapshot();
    const origin = clamp(playback.currentTime, 0, this.durationSeconds);
    if (playback.playing) this.playback.pause();
    this.video.pause?.();
    this.audio.pause?.();
    if (this.audioPolicy === "muted" && this.audio.setMasterMuted) {
      this.restoreMasterMuted = this.audio.getSnapshot?.().masterMuted ?? false;
      this.audio.setMasterMuted(true);
    }
    this.playhead.beginDrag();
    this.throttle = { lastPreviewAtMs: null, lastPreviewTimeSeconds: null };
    return this.commit({ ...this.state, status: "scrubbing", originTimeSeconds: origin, previewTimeSeconds: origin, committedTimeSeconds: origin, previewFrame: toFrame(origin, this.fps), pointerPixel: null, wasPlayingBeforeScrub: playback.playing }, "scrub-started");
  }

  previewAtPixel(pixel: number): TimelineScrubbingSnapshot {
    this.assertScrubbing();
    const preview = this.playhead.dragToPixel(finiteNumber(pixel, "pixel"));
    return this.preview(preview.timeSeconds, pixel, false);
  }

  previewAtTime(timeSeconds: number): TimelineScrubbingSnapshot {
    this.assertScrubbing();
    const time = this.normalizeTime(timeSeconds);
    this.playhead.moveToTime(time);
    return this.preview(time, null, false);
  }

  flushPreview(): TimelineScrubbingSnapshot {
    this.assertScrubbing();
    return this.preview(this.state.previewTimeSeconds, this.state.pointerPixel, true);
  }

  async commitScrub(): Promise<TimelineScrubbingSnapshot> {
    this.assertActive();
    if (this.state.status !== "scrubbing") return this.getSnapshot();
    this.preview(this.state.previewTimeSeconds, this.state.pointerPixel, true);
    const finalTime = this.state.previewTimeSeconds;
    this.state = { ...this.state, status: "committing" };
    this.playback.seek(finalTime);
    this.playhead.endDrag();
    this.video.seek(finalTime, "scrub-commit");
    this.audio.seek(finalTime);
    this.restoreAudioMute();
    const shouldResume = this.state.wasPlayingBeforeScrub && this.state.resumePlaybackOnCommit;
    if (shouldResume) {
      await Promise.resolve(this.playback.play());
      await Promise.resolve(this.video.play?.());
      await Promise.resolve(this.audio.play?.());
    }
    return this.commit({ ...this.state, status: "ready", committedTimeSeconds: finalTime, previewTimeSeconds: finalTime, previewFrame: toFrame(finalTime, this.fps), pointerPixel: null }, "committed");
  }

  async cancelScrub(): Promise<TimelineScrubbingSnapshot> {
    this.assertActive();
    if (this.state.status !== "scrubbing") return this.getSnapshot();
    const origin = this.state.originTimeSeconds;
    this.playhead.cancelDrag();
    this.playhead.moveToTime(origin);
    this.video.seek(origin, "scrub-cancel");
    this.audio.seek(origin);
    this.restoreAudioMute();
    if (this.state.wasPlayingBeforeScrub) {
      await Promise.resolve(this.playback.play());
      await Promise.resolve(this.video.play?.());
      await Promise.resolve(this.audio.play?.());
    }
    return this.commit({ ...this.state, status: "cancelled", previewTimeSeconds: origin, committedTimeSeconds: origin, previewFrame: toFrame(origin, this.fps), pointerPixel: null }, "cancelled");
  }

  syncFromPlayback(timeSeconds: number): TimelineScrubbingSnapshot {
    this.assertActive();
    if (this.state.status === "scrubbing") return this.getSnapshot();
    const time = this.normalizeTime(timeSeconds);
    return this.commit({ ...this.state, previewTimeSeconds: time, committedTimeSeconds: time, previewFrame: toFrame(time, this.fps) }, "configured");
  }

  setResumePlaybackOnCommit(value: boolean): TimelineScrubbingSnapshot { this.assertActive(); return this.commit({ ...this.state, resumePlaybackOnCommit: Boolean(value) }, "configured"); }
  syncDuration(value: number): TimelineScrubbingSnapshot { return this.configure({ durationSeconds: value }); }
  syncFrameRate(value: number): TimelineScrubbingSnapshot { return this.configure({ fps: value }); }
  syncViewport(value: number): TimelineScrubbingSnapshot { this.playhead.setViewport?.(value); return this.commit({ ...this.state }, "configured"); }
  syncZoom(value: number): TimelineScrubbingSnapshot { this.playhead.setZoom?.(value); return this.commit({ ...this.state }, "configured"); }
  syncScroll(value: number): TimelineScrubbingSnapshot { this.playhead.setScrollOffset?.(value); return this.commit({ ...this.state }, "configured"); }

  reset(): TimelineScrubbingSnapshot {
    this.assertActive(); this.restoreAudioMute(); this.throttle = { lastPreviewAtMs: null, lastPreviewTimeSeconds: null };
    const time = clamp(this.playback.getSnapshot().currentTime, 0, this.durationSeconds);
    return this.commit({ ...this.state, status: "idle", previewTimeSeconds: time, committedTimeSeconds: time, originTimeSeconds: time, wasPlayingBeforeScrub: false, previewFrame: toFrame(time, this.fps), pointerPixel: null }, "reset");
  }
  dispose(): void { if (this.disposed) return; this.restoreAudioMute(); this.listeners.clear(); this.disposed = true; this.state = { ...this.state, status: "disposed", updatedAt: this.now() }; }

  private preview(timeSeconds: number, pointerPixel: number | null, force: boolean): TimelineScrubbingSnapshot {
    const time = this.normalizeTime(timeSeconds); const nowMs = this.nowMs();
    if (!force && !shouldEmitScrubPreview(this.throttle, nowMs, time, this.previewIntervalMs, this.minimumDeltaSeconds)) {
      this.state = { ...this.state, previewTimeSeconds: time, previewFrame: toFrame(time, this.fps), pointerPixel };
      return this.getSnapshot();
    }
    this.video.seek(time, "scrub-preview");
    this.audio.seek(time);
    this.throttle = { lastPreviewAtMs: nowMs, lastPreviewTimeSeconds: time };
    return this.commit({ ...this.state, previewTimeSeconds: time, previewFrame: toFrame(time, this.fps), pointerPixel }, "previewed");
  }
  private normalizeTime(value: number): number { let time = clamp(finiteNumber(value, "timeSeconds"), 0, this.durationSeconds); if (this.snapToFrames) time = clamp(Math.round(time * this.fps) / this.fps, 0, this.durationSeconds); return time; }
  private restoreAudioMute(): void { if (this.restoreMasterMuted !== null && this.audio.setMasterMuted) this.audio.setMasterMuted(this.restoreMasterMuted); this.restoreMasterMuted = null; }
  private commit(candidate: TimelineScrubbingSnapshot, type: TimelineScrubbingEventType): TimelineScrubbingSnapshot { const previous = { ...this.state }; const occurredAt = this.now(); this.state = { ...candidate, stateRevision: this.state.stateRevision + 1, updatedAt: occurredAt }; const current = { ...this.state }; const event: TimelineScrubbingEvent = { type, stateRevision: current.stateRevision, occurredAt }; for (const listener of this.listeners) listener({ ...current }, { ...previous }, { ...event }); return current; }
  private assertScrubbing(): void { this.assertActive(); if (this.state.status !== "scrubbing") throw new Error("Timeline scrubbing has not started."); }
  private assertActive(): void { if (this.disposed) throw new Error("Timeline scrubbing runtime has been disposed."); }
}

export function createTimelineScrubbingRuntime(playback: ScrubbingPlaybackPort, playhead: ScrubbingPlayheadPort, video: ScrubbingVideoPort, audio: ScrubbingAudioPort, configuration: TimelineScrubbingConfiguration, options: TimelineScrubbingRuntimeOptions = {}): TimelineScrubbingRuntime { return new TimelineScrubbingRuntime(playback, playhead, video, audio, configuration, options); }
function toFrame(time: number, fps: number): number { return Math.round(time * fps); }
function clamp(value: number, min: number, max: number): number { return Math.min(max, Math.max(min, value)); }
function finiteNumber(value: number, name: string): number { if (!Number.isFinite(value)) throw new Error(`${name} must be finite.`); return value; }
function finiteNonNegative(value: number, name: string): number { finiteNumber(value, name); if (value < 0) throw new Error(`${name} must be non-negative.`); return value; }
function finitePositive(value: number, name: string): number { finiteNumber(value, name); if (value <= 0) throw new Error(`${name} must be positive.`); return value; }
