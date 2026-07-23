import type { PlaybackDirection } from "../contracts/professional-playback-contracts";

export class PlaybackSpeedRuntime {
  private speed: number;
  private direction: PlaybackDirection = "forward";

  constructor(
    initialSpeed = 1,
    private readonly minSpeed = 0.25,
    private readonly maxSpeed = 8,
  ) {
    this.speed = this.clamp(initialSpeed);
  }

  getSpeed(): number { return this.speed; }
  getDirection(): PlaybackDirection { return this.direction; }

  setSpeed(speed: number): number {
    if (!Number.isFinite(speed) || speed <= 0) throw new Error("Playback speed must be a positive finite number.");
    this.speed = this.clamp(speed);
    return this.speed;
  }

  setDirection(direction: PlaybackDirection): PlaybackDirection {
    this.direction = direction;
    return direction;
  }

  shuttleForward(): number {
    this.direction = "forward";
    this.speed = this.nextShuttleSpeed(this.speed);
    return this.speed;
  }

  shuttleReverse(): number {
    this.direction = "reverse";
    this.speed = this.nextShuttleSpeed(this.speed);
    return this.speed;
  }

  pauseShuttle(): void {
    this.speed = 1;
  }

  private nextShuttleSpeed(current: number): number {
    const ladder = [0.25, 0.5, 1, 1.5, 2, 4, 8].filter((value) => value >= this.minSpeed && value <= this.maxSpeed);
    const index = ladder.findIndex((value) => value > current + Number.EPSILON);
    return index === -1 ? ladder[ladder.length - 1] ?? this.maxSpeed : ladder[index];
  }

  private clamp(value: number): number {
    return Math.min(this.maxSpeed, Math.max(this.minSpeed, value));
  }
}
