import type { VideoPreviewEventName, VideoPreviewPort } from "../contracts";

export class HtmlVideoPreviewAdapter implements VideoPreviewPort {
  constructor(private readonly element: HTMLVideoElement) {}

  get currentTime(): number { return this.element.currentTime; }
  get duration(): number { return this.element.duration; }
  get paused(): boolean { return this.element.paused; }
  get seeking(): boolean { return this.element.seeking; }
  get ended(): boolean { return this.element.ended; }
  get playbackRate(): number { return this.element.playbackRate; }

  play(): Promise<void> { return this.element.play(); }
  pause(): void { this.element.pause(); }
  setCurrentTime(value: number): void { this.element.currentTime = value; }
  setPlaybackRate(value: number): void { this.element.playbackRate = value; }

  subscribe(event: VideoPreviewEventName, listener: () => void): () => void {
    this.element.addEventListener(event, listener);
    return () => this.element.removeEventListener(event, listener);
  }
}

export function createHtmlVideoPreviewAdapter(element: HTMLVideoElement): HtmlVideoPreviewAdapter {
  return new HtmlVideoPreviewAdapter(element);
}
