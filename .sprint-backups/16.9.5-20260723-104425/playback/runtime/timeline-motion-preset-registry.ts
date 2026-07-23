import type { TimelineKeyframe, TimelineMotionPreset } from "../contracts/timeline-effects-animation-contracts";

const builtIns: readonly TimelineMotionPreset[] = Object.freeze([
  { presetId: "fade-in", label: "Fade In", durationSeconds: 0.35, keyframes: [
    { property: "opacity", timeSeconds: 0, value: 0, interpolation: "ease-out" },
    { property: "opacity", timeSeconds: 0.35, value: 1, interpolation: "linear" },
  ] },
  { presetId: "fade-out", label: "Fade Out", durationSeconds: 0.35, keyframes: [
    { property: "opacity", timeSeconds: 0, value: 1, interpolation: "ease-in" },
    { property: "opacity", timeSeconds: 0.35, value: 0, interpolation: "linear" },
  ] },
  { presetId: "zoom-in", label: "Zoom In", durationSeconds: 0.6, keyframes: [
    { property: "scale-x", timeSeconds: 0, value: 0.92, interpolation: "ease-out" },
    { property: "scale-y", timeSeconds: 0, value: 0.92, interpolation: "ease-out" },
    { property: "scale-x", timeSeconds: 0.6, value: 1, interpolation: "linear" },
    { property: "scale-y", timeSeconds: 0.6, value: 1, interpolation: "linear" },
  ] },
  { presetId: "slide-up", label: "Slide Up", durationSeconds: 0.45, keyframes: [
    { property: "position-y", timeSeconds: 0, value: 80, interpolation: "ease-out" },
    { property: "position-y", timeSeconds: 0.45, value: 0, interpolation: "linear" },
  ] },
]);

export class TimelineMotionPresetRegistry {
  private readonly presets = new Map<string, TimelineMotionPreset>(builtIns.map((preset) => [preset.presetId, preset]));
  register(preset: TimelineMotionPreset): void { this.presets.set(preset.presetId, Object.freeze({ ...preset, keyframes: Object.freeze([...preset.keyframes]) })); }
  remove(presetId: string): boolean { return this.presets.delete(presetId); }
  get(presetId: string): TimelineMotionPreset | null { return this.presets.get(presetId) ?? null; }
  list(): readonly TimelineMotionPreset[] { return Object.freeze([...this.presets.values()].sort((a, b) => a.label.localeCompare(b.label))); }

  instantiate(presetId: string, clipId: string, startSeconds = 0, idFactory: () => string = () => `${Date.now()}-${Math.random()}`): readonly TimelineKeyframe[] {
    const preset = this.get(presetId);
    if (!preset) throw new Error(`Unknown motion preset: ${presetId}`);
    return Object.freeze(preset.keyframes.map((keyframe) => Object.freeze({ ...keyframe, clipId, timeSeconds: startSeconds + keyframe.timeSeconds, keyframeId: idFactory() })));
  }
}
