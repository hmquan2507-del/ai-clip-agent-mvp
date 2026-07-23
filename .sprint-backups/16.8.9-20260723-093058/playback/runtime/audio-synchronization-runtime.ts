import {
  AUDIO_SYNCHRONIZATION_CONTRACT_VERSION,
  type AudioPreviewEventName,
  type AudioPreviewPort,
  type AudioSynchronizationConfiguration,
  type AudioSynchronizationEvent,
  type AudioSynchronizationEventType,
  type AudioSynchronizationListener,
  type AudioSynchronizationSnapshot,
  type AudioTrackDescriptor,
  type AudioTrackSnapshot,
} from "../contracts";
import type { PlaybackSessionRuntime } from "./playback-session-runtime";
import {
  clampUnit,
  createAudioDriftThreshold,
  isAudioTrackActive,
  timelineToAudioSourceTime,
} from "./audio-drift-model";

interface AttachedTrack {
  descriptor: AudioTrackDescriptor;
  port: AudioPreviewPort;
  unsubscribe: Array<() => void>;
  buffering: boolean;
  driftSeconds: number;
  errorMessage: string | null;
  suppressSeek: boolean;
}

export interface AudioSynchronizationRuntimeOptions { now?: () => string; }

export class AudioSynchronizationRuntime {
  private state: AudioSynchronizationSnapshot;
  private readonly listeners = new Set<AudioSynchronizationListener>();
  private readonly tracks = new Map<string, AttachedTrack>();
  private readonly now: () => string;
  private readonly driftThreshold: number;
  private readonly largeDriftThreshold: number;
  private disposed = false;

  constructor(
    private readonly playback: PlaybackSessionRuntime,
    configuration: AudioSynchronizationConfiguration,
    options: AudioSynchronizationRuntimeOptions = {},
  ) {
    this.driftThreshold = createAudioDriftThreshold(configuration.fps, configuration.driftThreshold);
    this.largeDriftThreshold = Math.max(configuration.largeDriftThreshold ?? 0.5, this.driftThreshold);
    this.now = options.now ?? (() => new Date().toISOString());
    this.state = {
      contractVersion: AUDIO_SYNCHRONIZATION_CONTRACT_VERSION,
      status: "idle",
      currentTimeSeconds: 0,
      playbackRate: 1,
      masterVolume: clampUnit(configuration.masterVolume ?? 1),
      masterMuted: Boolean(configuration.masterMuted),
      activeTrackIds: [], bufferingTrackIds: [], driftedTrackIds: [], tracks: [],
      stateRevision: 0, updatedAt: null,
    };
  }

  getSnapshot(): AudioSynchronizationSnapshot { return cloneSnapshot(this.state); }
  getState(): AudioSynchronizationSnapshot { return this.getSnapshot(); }
  subscribe(listener: AudioSynchronizationListener): () => void {
    this.assertActive(); this.listeners.add(listener); return () => this.listeners.delete(listener);
  }

  attachTrack(descriptor: AudioTrackDescriptor, port: AudioPreviewPort): AudioSynchronizationSnapshot {
    this.assertActive();
    validateDescriptor(descriptor);
    this.detachTrack(descriptor.id, false);
    const copy = { ...descriptor, volume: clampUnit(descriptor.volume) };
    const attached: AttachedTrack = { descriptor: copy, port, unsubscribe: [], buffering: false, driftSeconds: 0, errorMessage: null, suppressSeek: false };
    for (const event of ["loadedmetadata","timeupdate","seeking","seeked","ended","waiting","playing","pause","error"] as const) {
      attached.unsubscribe.push(port.subscribe(event, () => this.handleAudioEvent(copy.id, event)));
    }
    this.tracks.set(copy.id, attached);
    this.applyTrackMix(attached);
    return this.commit("track-attached", copy.id, "ready");
  }

  detachTrack(trackId: string, emit = true): AudioSynchronizationSnapshot {
    this.assertActive();
    const track = this.tracks.get(trackId);
    if (!track) return this.getSnapshot();
    while (track.unsubscribe.length) track.unsubscribe.pop()?.();
    if (!track.port.paused) track.port.pause();
    this.tracks.delete(trackId);
    return emit ? this.commit("track-detached", trackId, this.tracks.size ? "ready" : "idle") : this.rebuildState(this.state.status);
  }

  detachAll(): AudioSynchronizationSnapshot {
    this.assertActive();
    for (const track of this.tracks.values()) {
      while (track.unsubscribe.length) track.unsubscribe.pop()?.();
      if (!track.port.paused) track.port.pause();
    }
    this.tracks.clear();
    return this.commit("tracks-detached", undefined, "idle");
  }

  async play(): Promise<AudioSynchronizationSnapshot> {
    this.assertActive();
    const playback = this.playback.play();
    await this.syncTracks(playback.currentTime, true);
    return this.commit("play-synced", undefined, "playing");
  }

  pause(): AudioSynchronizationSnapshot {
    this.assertActive(); this.playback.pause();
    for (const track of this.tracks.values()) if (!track.port.paused) track.port.pause();
    return this.commit("pause-synced", undefined, "paused");
  }

  stop(): AudioSynchronizationSnapshot {
    this.assertActive(); const playback = this.playback.stop();
    for (const track of this.tracks.values()) {
      if (!track.port.paused) track.port.pause();
      this.setTrackTime(track, timelineToAudioSourceTime(playback.currentTime, track.descriptor.startTimeSeconds, track.descriptor.sourceOffsetSeconds));
    }
    return this.commit("stop-synced", undefined, "stopped", playback.currentTime);
  }

  seek(time: number): AudioSynchronizationSnapshot {
    this.assertActive(); const playback = this.playback.seek(time);
    for (const track of this.tracks.values()) {
      const expected = timelineToAudioSourceTime(playback.currentTime, track.descriptor.startTimeSeconds, track.descriptor.sourceOffsetSeconds);
      this.setTrackTime(track, expected);
    }
    return this.commit("seek-synced", undefined, "seeking", playback.currentTime);
  }

  setPlaybackRate(rate: number): AudioSynchronizationSnapshot {
    this.assertActive(); const playback = this.playback.setSpeed(rate);
    for (const track of this.tracks.values()) if (Math.abs(track.port.playbackRate - playback.speed) > Number.EPSILON) track.port.setPlaybackRate(playback.speed);
    return this.commit("rate-synced", undefined, this.state.status, undefined, playback.speed);
  }

  setMasterVolume(value: number): AudioSynchronizationSnapshot {
    this.assertActive(); this.state = { ...this.state, masterVolume: clampUnit(value) }; this.refreshMix();
    return this.commit("volume-changed", undefined, this.state.status);
  }
  setMasterMuted(value: boolean): AudioSynchronizationSnapshot {
    this.assertActive(); this.state = { ...this.state, masterMuted: Boolean(value) }; this.refreshMix();
    return this.commit("mute-changed", undefined, this.state.status);
  }
  setTrackVolume(trackId: string, value: number): AudioSynchronizationSnapshot {
    const track = this.requireTrack(trackId); track.descriptor = { ...track.descriptor, volume: clampUnit(value) }; this.refreshMix();
    return this.commit("volume-changed", trackId, this.state.status);
  }
  setTrackMuted(trackId: string, value: boolean): AudioSynchronizationSnapshot {
    const track = this.requireTrack(trackId); track.descriptor = { ...track.descriptor, muted: Boolean(value) }; this.refreshMix();
    return this.commit("mute-changed", trackId, this.state.status);
  }
  setTrackSolo(trackId: string, value: boolean): AudioSynchronizationSnapshot {
    const track = this.requireTrack(trackId); track.descriptor = { ...track.descriptor, solo: Boolean(value) }; this.refreshMix();
    return this.commit("solo-changed", trackId, this.state.status);
  }

  async syncFromPlayback(): Promise<AudioSynchronizationSnapshot> {
    this.assertActive(); const playback = this.playback.getSnapshot();
    await this.syncTracks(playback.currentTime, playback.playing);
    return this.commit(playback.playing ? "play-synced" : "pause-synced", undefined, playback.playing ? "playing" : "paused", playback.currentTime, playback.speed);
  }

  reset(): AudioSynchronizationSnapshot {
    this.assertActive(); this.playback.reset();
    for (const track of this.tracks.values()) {
      if (!track.port.paused) track.port.pause();
      this.setTrackTime(track, track.descriptor.sourceOffsetSeconds);
      track.buffering = false; track.driftSeconds = 0; track.errorMessage = null;
    }
    this.state = { ...this.state, currentTimeSeconds: 0, playbackRate: 1, masterVolume: 1, masterMuted: false };
    this.refreshMix();
    return this.commit("reset", undefined, this.tracks.size ? "ready" : "idle", 0, 1);
  }

  dispose(): void {
    if (this.disposed) return;
    for (const track of this.tracks.values()) { while (track.unsubscribe.length) track.unsubscribe.pop()?.(); if (!track.port.paused) track.port.pause(); }
    this.tracks.clear(); this.listeners.clear(); this.disposed = true;
    this.state = { ...this.state, status: "disposed", tracks: [], activeTrackIds: [], bufferingTrackIds: [], driftedTrackIds: [], updatedAt: this.now() };
  }

  private async syncTracks(playbackTime: number, shouldPlay: boolean): Promise<void> {
    const playback = this.playback.getSnapshot();
    for (const track of this.tracks.values()) {
      const active = this.isTrackAudible(track, playbackTime);
      const expected = timelineToAudioSourceTime(playbackTime, track.descriptor.startTimeSeconds, track.descriptor.sourceOffsetSeconds);
      track.driftSeconds = track.port.currentTime - expected;
      if (active && Math.abs(track.driftSeconds) > this.driftThreshold) this.setTrackTime(track, expected);
      if (Math.abs(track.port.playbackRate - playback.speed) > Number.EPSILON) track.port.setPlaybackRate(playback.speed);
      this.applyTrackMix(track);
      if (active && shouldPlay) {
        if (track.port.paused) { try { await track.port.play(); } catch (error) { track.errorMessage = error instanceof Error ? error.message : String(error); } }
      } else if (!track.port.paused) track.port.pause();
    }
  }

  private handleAudioEvent(trackId: string, event: AudioPreviewEventName): void {
    const track = this.tracks.get(trackId); if (!track || this.disposed) return;
    if (event === "waiting") { track.buffering = true; this.commit("buffering-started", trackId, "buffering"); return; }
    if (event === "playing") { track.buffering = false; this.commit("buffering-ended", trackId, "playing"); return; }
    if (event === "seeked" && track.suppressSeek) { track.suppressSeek = false; return; }
    if (event === "error") { track.errorMessage = "Audio preview media error."; this.commit("error", trackId, "error"); }
  }

  private refreshMix(): void { for (const track of this.tracks.values()) this.applyTrackMix(track); }
  private applyTrackMix(track: AttachedTrack): void {
    const anySolo = [...this.tracks.values()].some(item => item.descriptor.solo);
    const audible = track.descriptor.enabled && !this.state.masterMuted && !track.descriptor.muted && (!anySolo || track.descriptor.solo);
    const volume = clampUnit(this.state.masterVolume * track.descriptor.volume * (audible ? 1 : 0));
    if (Math.abs(track.port.volume - volume) > Number.EPSILON) track.port.setVolume(volume);
    if (track.port.muted !== !audible) track.port.setMuted(!audible);
  }
  private isTrackAudible(track: AttachedTrack, time: number): boolean {
    const anySolo = [...this.tracks.values()].some(item => item.descriptor.solo);
    return isAudioTrackActive(time, track.descriptor.startTimeSeconds, track.descriptor.endTimeSeconds)
      && track.descriptor.enabled && !this.state.masterMuted && !track.descriptor.muted && (!anySolo || track.descriptor.solo);
  }
  private setTrackTime(track: AttachedTrack, value: number): void {
    const duration = Number.isFinite(track.port.duration) && track.port.duration >= 0 ? track.port.duration : Number.MAX_SAFE_INTEGER;
    const bounded = Math.min(duration, Math.max(0, value));
    if (Math.abs(track.port.currentTime - bounded) <= this.driftThreshold) return;
    track.suppressSeek = true; track.port.setCurrentTime(bounded);
  }
  private requireTrack(id: string): AttachedTrack { this.assertActive(); const track = this.tracks.get(id); if (!track) throw new Error(`Audio track not attached: ${id}`); return track; }
  private rebuildState(status: AudioSynchronizationSnapshot["status"], time = this.playback.getSnapshot().currentTime, rate = this.playback.getSnapshot().speed): AudioSynchronizationSnapshot {
    const anySolo = [...this.tracks.values()].some(item => item.descriptor.solo);
    const tracks: AudioTrackSnapshot[] = [...this.tracks.values()].map(track => {
      const active = isAudioTrackActive(time, track.descriptor.startTimeSeconds, track.descriptor.endTimeSeconds);
      const audible = track.descriptor.enabled && !this.state.masterMuted && !track.descriptor.muted && (!anySolo || track.descriptor.solo);
      return { ...track.descriptor, attached: true, active, buffering: track.buffering, driftSeconds: track.driftSeconds, effectiveVolume: clampUnit(this.state.masterVolume * track.descriptor.volume * (audible ? 1 : 0)), sourceTimeSeconds: timelineToAudioSourceTime(time, track.descriptor.startTimeSeconds, track.descriptor.sourceOffsetSeconds), errorMessage: track.errorMessage };
    });
    return { ...this.state, status, currentTimeSeconds: time, playbackRate: rate, tracks, activeTrackIds: tracks.filter(t => t.active && t.effectiveVolume > 0).map(t => t.id), bufferingTrackIds: tracks.filter(t => t.buffering).map(t => t.id), driftedTrackIds: tracks.filter(t => Math.abs(t.driftSeconds) > this.driftThreshold).map(t => t.id) };
  }
  private commit(type: AudioSynchronizationEventType, trackId?: string, status: AudioSynchronizationSnapshot["status"] = this.state.status, time?: number, rate?: number): AudioSynchronizationSnapshot {
    const previous = cloneSnapshot(this.state); const occurredAt = this.now();
    this.state = { ...this.rebuildState(status, time, rate), stateRevision: this.state.stateRevision + 1, updatedAt: occurredAt };
    const current = cloneSnapshot(this.state); const event: AudioSynchronizationEvent = { type, trackId, stateRevision: current.stateRevision, occurredAt };
    for (const listener of this.listeners) listener(cloneSnapshot(current), cloneSnapshot(previous), { ...event });
    return current;
  }
  private assertActive(): void { if (this.disposed) throw new Error("Audio synchronization runtime has been disposed."); }
}

export function createAudioSynchronizationRuntime(playback: PlaybackSessionRuntime, configuration: AudioSynchronizationConfiguration, options: AudioSynchronizationRuntimeOptions = {}): AudioSynchronizationRuntime {
  return new AudioSynchronizationRuntime(playback, configuration, options);
}

function validateDescriptor(descriptor: AudioTrackDescriptor): void {
  if (!descriptor.id.trim()) throw new Error("track id is required.");
  if (!Number.isFinite(descriptor.startTimeSeconds) || descriptor.startTimeSeconds < 0) throw new Error("startTimeSeconds must be non-negative.");
  if (!Number.isFinite(descriptor.endTimeSeconds) || descriptor.endTimeSeconds <= descriptor.startTimeSeconds) throw new Error("endTimeSeconds must be greater than startTimeSeconds.");
  if (!Number.isFinite(descriptor.sourceOffsetSeconds) || descriptor.sourceOffsetSeconds < 0) throw new Error("sourceOffsetSeconds must be non-negative.");
}
function cloneSnapshot(state: AudioSynchronizationSnapshot): AudioSynchronizationSnapshot { return { ...state, activeTrackIds: [...state.activeTrackIds], bufferingTrackIds: [...state.bufferingTrackIds], driftedTrackIds: [...state.driftedTrackIds], tracks: state.tracks.map(track => ({ ...track })) }; }
