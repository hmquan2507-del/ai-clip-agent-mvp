import type { TimelineEffectsAnimationFrame } from "../contracts/timeline-effects-animation-contracts";
import type { TimelineEffectsPreviewPort } from "../contracts/timeline-effects-workspace-contracts";

export class HtmlTimelineEffectsPreviewAdapter implements TimelineEffectsPreviewPort {
  constructor(private readonly element: HTMLElement) {}

  applyFrame(frame: TimelineEffectsAnimationFrame): void {
    const value = frame.properties;
    const x = value["position-x"] ?? 0;
    const y = value["position-y"] ?? 0;
    const scaleX = value["scale-x"] ?? 1;
    const scaleY = value["scale-y"] ?? 1;
    const rotation = value.rotation ?? 0;
    this.element.style.transform = `translate(${x}px, ${y}px) scale(${scaleX}, ${scaleY}) rotate(${rotation}deg)`;
    this.element.style.opacity = String(value.opacity ?? 1);
    const filters = [
      value.blur === undefined ? "" : `blur(${value.blur}px)`,
      value.brightness === undefined ? "" : `brightness(${value.brightness})`,
      value.contrast === undefined ? "" : `contrast(${value.contrast})`,
      value.saturation === undefined ? "" : `saturate(${value.saturation})`,
    ].filter(Boolean);
    this.element.style.filter = filters.join(" ");
    if (this.element instanceof HTMLMediaElement && value.volume !== undefined) this.element.volume = Math.max(0, Math.min(1, value.volume));
    this.element.dataset.effectsClipId = frame.clipId;
  }

  clear(): void {
    this.element.style.removeProperty("transform");
    this.element.style.removeProperty("opacity");
    this.element.style.removeProperty("filter");
    delete this.element.dataset.effectsClipId;
  }
}

export function createHtmlTimelineEffectsPreviewAdapter(element: HTMLElement): HtmlTimelineEffectsPreviewAdapter {
  return new HtmlTimelineEffectsPreviewAdapter(element);
}
