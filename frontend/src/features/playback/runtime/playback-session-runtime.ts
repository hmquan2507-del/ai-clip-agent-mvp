import {
  PLAYBACK_SESSION_CONTRACT_VERSION,
  type PlaybackDirection,
  type PlaybackSessionConfiguration,
  type PlaybackSessionEvent,
  type PlaybackSessionEventType,
  type PlaybackSessionListener,
  type PlaybackSessionState,
} from "../contracts";
import {
  assertNonNegativeNumber,
  assertPositiveNumber,
  clampPlaybackTime,
  frameToTime,
  timeToFrame,
} from "./playback-time-model";

export interface PlaybackSessionRuntimeOptions {
  now?: () => string;
}

export class PlaybackSessionRuntime {
  private state: PlaybackSessionState;
  private readonly listeners = new Set<PlaybackSessionListener>();
  private readonly now: () => string;
  private disposed = false;

  constructor(
    configuration: PlaybackSessionConfiguration,
    options: PlaybackSessionRuntimeOptions = {},
  ) {
    const duration = assertNonNegativeNumber(configuration.duration, "duration");
    const fps = assertPositiveNumber(configuration.fps, "fps");
    const speed = normalizeSpeed(configuration.initialSpeed ?? 1);
    const direction = normalizeDirection(configuration.initialDirection ?? 1);
    const currentTime = clampPlaybackTime(configuration.initialTime ?? 0, duration);

    this.now = options.now ?? (() => new Date().toISOString());
    this.state = {
      contractVersion: PLAYBACK_SESSION_CONTRACT_VERSION,
      status: "idle",
      duration,
      fps,
      currentTime,
      currentFrame: timeToFrame(currentTime, fps, duration),
      speed,
      loop: configuration.initialLoop ?? false,
      direction,
      playing: false,
      stateRevision: 0,
      updatedAt: null,
    };
  }

  getSnapshot(): PlaybackSessionState {
    return cloneState(this.state);
  }

  getState(): PlaybackSessionState {
    return this.getSnapshot();
  }

  subscribe(listener: PlaybackSessionListener): () => void {
    this.assertActive();
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  ready(): PlaybackSessionState {
    this.assertActive();
    return this.commit(
      {
        ...this.state,
        status: "ready",
        playing: false,
      },
      "ready",
    );
  }

  play(): PlaybackSessionState {
    this.assertActive();
    let currentTime = this.state.currentTime;
    if (this.state.direction === 1 && currentTime >= this.state.duration) currentTime = 0;
    if (this.state.direction === -1 && currentTime <= 0) currentTime = this.state.duration;
    return this.commit(
      {
        ...this.state,
        currentTime,
        currentFrame: timeToFrame(currentTime, this.state.fps, this.state.duration),
        status: "playing",
        playing: true,
      },
      "started",
    );
  }

  pause(): PlaybackSessionState {
    this.assertActive();
    return this.commit(
      { ...this.state, status: "paused", playing: false },
      "paused",
    );
  }

  stop(): PlaybackSessionState {
    this.assertActive();
    const currentTime = this.state.direction === 1 ? 0 : this.state.duration;
    return this.commit(
      {
        ...this.state,
        currentTime,
        currentFrame: timeToFrame(currentTime, this.state.fps, this.state.duration),
        status: "stopped",
        playing: false,
      },
      "stopped",
    );
  }

  seek(time: number): PlaybackSessionState {
    this.assertActive();
    const currentTime = clampPlaybackTime(time, this.state.duration);
    return this.commit(
      {
        ...this.state,
        currentTime,
        currentFrame: timeToFrame(currentTime, this.state.fps, this.state.duration),
        status: "seeking",
        playing: false,
      },
      "seeked",
    );
  }

  setSpeed(speed: number): PlaybackSessionState {
    this.assertActive();
    return this.commit({ ...this.state, speed: normalizeSpeed(speed) }, "speed-changed");
  }

  setDirection(direction: PlaybackDirection): PlaybackSessionState {
    this.assertActive();
    return this.commit({ ...this.state, direction: normalizeDirection(direction) }, "speed-changed");
  }

  setLoop(loop: boolean): PlaybackSessionState {
    this.assertActive();
    return this.commit({ ...this.state, loop: Boolean(loop) }, "loop-changed");
  }

  toggleLoop(): PlaybackSessionState {
    return this.setLoop(!this.state.loop);
  }

  stepForward(frames = 1): PlaybackSessionState {
    return this.stepByFrames(Math.abs(normalizeFrameCount(frames)));
  }

  stepBackward(frames = 1): PlaybackSessionState {
    return this.stepByFrames(-Math.abs(normalizeFrameCount(frames)));
  }

  advance(deltaSeconds: number): PlaybackSessionState {
    this.assertActive();
    assertNonNegativeNumber(deltaSeconds, "deltaSeconds");
    if (!this.state.playing || deltaSeconds === 0) return this.getSnapshot();

    const signedDelta = deltaSeconds * this.state.speed * this.state.direction;
    const candidate = this.state.currentTime + signedDelta;
    const reachedEnd = this.state.direction === 1 && candidate >= this.state.duration;
    const reachedStart = this.state.direction === -1 && candidate <= 0;

    if (reachedEnd || reachedStart) {
      if (this.state.loop && this.state.duration > 0) {
        const wrapped = wrapTime(candidate, this.state.duration);
        return this.commit(
          {
            ...this.state,
            currentTime: wrapped,
            currentFrame: timeToFrame(wrapped, this.state.fps, this.state.duration),
            status: "playing",
            playing: true,
          },
          "looped",
        );
      }
      const boundary = this.state.direction === 1 ? this.state.duration : 0;
      return this.commit(
        {
          ...this.state,
          currentTime: boundary,
          currentFrame: timeToFrame(boundary, this.state.fps, this.state.duration),
          status: "completed",
          playing: false,
        },
        "completed",
      );
    }

    return this.commit(
      {
        ...this.state,
        currentTime: candidate,
        currentFrame: timeToFrame(candidate, this.state.fps, this.state.duration),
      },
      "advanced",
    );
  }

  reset(): PlaybackSessionState {
    this.assertActive();
    return this.commit(
      {
        ...this.state,
        status: "idle",
        currentTime: 0,
        currentFrame: 0,
        speed: 1,
        loop: false,
        direction: 1,
        playing: false,
      },
      "reset",
    );
  }

  dispose(): void {
    if (this.disposed) return;
    this.listeners.clear();
    this.disposed = true;
    this.state = {
      ...this.state,
      status: "disposed",
      playing: false,
      updatedAt: this.now(),
    };
  }

  private stepByFrames(deltaFrames: number): PlaybackSessionState {
    this.assertActive();
    const nextFrame = this.state.currentFrame + deltaFrames;
    const currentTime = frameToTime(nextFrame, this.state.fps, this.state.duration);
    return this.commit(
      {
        ...this.state,
        currentTime,
        currentFrame: timeToFrame(currentTime, this.state.fps, this.state.duration),
        status: "paused",
        playing: false,
      },
      "stepped",
    );
  }

  private commit(
    candidate: PlaybackSessionState,
    eventType: PlaybackSessionEventType,
  ): PlaybackSessionState {
    const previous = cloneState(this.state);
    const occurredAt = this.now();
    this.state = {
      ...candidate,
      stateRevision: this.state.stateRevision + 1,
      updatedAt: occurredAt,
    };
    const current = cloneState(this.state);
    const event: PlaybackSessionEvent = {
      type: eventType,
      stateRevision: current.stateRevision,
      occurredAt,
    };
    for (const listener of this.listeners) {
      listener(cloneState(current), cloneState(previous), { ...event });
    }
    return current;
  }

  private assertActive(): void {
    if (this.disposed) throw new Error("Playback session runtime has been disposed.");
  }
}

export function createPlaybackSessionRuntime(
  configuration: PlaybackSessionConfiguration,
  options: PlaybackSessionRuntimeOptions = {},
): PlaybackSessionRuntime {
  return new PlaybackSessionRuntime(configuration, options);
}

function normalizeSpeed(speed: number): number {
  assertPositiveNumber(speed, "speed");
  if (speed > 16) throw new Error("speed must be less than or equal to 16.");
  return speed;
}

function normalizeDirection(direction: PlaybackDirection): PlaybackDirection {
  if (direction !== 1 && direction !== -1) throw new Error("direction must be 1 or -1.");
  return direction;
}

function normalizeFrameCount(frames: number): number {
  assertPositiveNumber(frames, "frames");
  return Math.round(frames);
}

function wrapTime(time: number, duration: number): number {
  if (duration <= 0) return 0;
  return ((time % duration) + duration) % duration;
}

function cloneState(state: PlaybackSessionState): PlaybackSessionState {
  return { ...state };
}
