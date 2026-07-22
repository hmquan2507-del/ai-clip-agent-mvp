import type { AudioPreviewEventName, AudioPreviewPort } from "../contracts";

export class HtmlAudioPreviewAdapter implements AudioPreviewPort {
  constructor(private readonly element: HTMLAudioElement) {}
  get currentTime(): number { return this.element.currentTime; }
  get duration(): number { return this.element.duration; }
  get paused(): boolean { return this.element.paused; }
  get seeking(): boolean { return this.element.seeking; }
  get ended(): boolean { return this.element.ended; }
  get playbackRate(): number { return this.element.playbackRate; }
  get volume(): number { return this.element.volume; }
  get muted(): boolean { return this.element.muted; }
  play(): Promise<void> { return this.element.play(); }
  pause(): void { this.element.pause(); }
  setCurrentTime(value: number): void { this.element.currentTime = value; }
  setPlaybackRate(value: number): void { this.element.playbackRate = value; }
  setVolume(value: number): void { this.element.volume = value; }
  setMuted(value: boolean): void { this.element.muted = value; }
  subscribe(event: AudioPreviewEventName, listener: () => void): () => void {
    this.element.addEventListener(event, listener);
    return () => this.element.removeEventListener(event, listener);
  }
}

export function createHtmlAudioPreviewAdapter(element: HTMLAudioElement): HtmlAudioPreviewAdapter {
  return new HtmlAudioPreviewAdapter(element);
}
