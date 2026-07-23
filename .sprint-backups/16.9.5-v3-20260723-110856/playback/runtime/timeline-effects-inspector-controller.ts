import type {
  TimelineAnimatableProperty,
  TimelineInterpolation,
  TimelineInspectorEffectCatalogItem,
  TimelineInspectorPropertyDescriptor,
  TimelineInspectorTransitionCatalogItem,
} from "../contracts";

const PROPERTY_DESCRIPTORS: readonly TimelineInspectorPropertyDescriptor[] = Object.freeze<TimelineInspectorPropertyDescriptor[]>([
  { property: "position-x", label: "Position X", min: -1920, max: 1920, step: 1, defaultValue: 0, unit: "px" },
  { property: "position-y", label: "Position Y", min: -1080, max: 1080, step: 1, defaultValue: 0, unit: "px" },
  { property: "scale-x", label: "Scale X", min: 0, max: 4, step: 0.01, defaultValue: 1 },
  { property: "scale-y", label: "Scale Y", min: 0, max: 4, step: 0.01, defaultValue: 1 },
  { property: "rotation", label: "Rotation", min: -360, max: 360, step: 1, defaultValue: 0, unit: "°" },
  { property: "opacity", label: "Opacity", min: 0, max: 1, step: 0.01, defaultValue: 1 },
  { property: "volume", label: "Volume", min: 0, max: 2, step: 0.01, defaultValue: 1 },
  { property: "blur", label: "Blur", min: 0, max: 40, step: 0.1, defaultValue: 0, unit: "px" },
  { property: "brightness", label: "Brightness", min: 0, max: 3, step: 0.01, defaultValue: 1 },
  { property: "contrast", label: "Contrast", min: 0, max: 3, step: 0.01, defaultValue: 1 },
  { property: "saturation", label: "Saturation", min: 0, max: 3, step: 0.01, defaultValue: 1 },
]);

const EFFECT_CATALOG: readonly TimelineInspectorEffectCatalogItem[] = Object.freeze<TimelineInspectorEffectCatalogItem[]>([
  { kind: "blur", label: "Gaussian Blur", description: "Soften the image with adjustable blur.", defaultParameters: { amount: 8 } },
  { kind: "brightness", label: "Brightness", description: "Brighten or darken the selected clip.", defaultParameters: { amount: 1 } },
  { kind: "contrast", label: "Contrast", description: "Increase or reduce tonal separation.", defaultParameters: { amount: 1 } },
  { kind: "saturation", label: "Saturation", description: "Control color intensity.", defaultParameters: { amount: 1 } },
  { kind: "color-adjustment", label: "Color adjustment", description: "Apply combined color correction controls.", defaultParameters: { temperature: 0, tint: 0 } },
  { kind: "audio-gain", label: "Audio gain", description: "Adjust clip loudness without changing keyframes.", defaultParameters: { gain: 1 } },
]);

const TRANSITION_CATALOG: readonly TimelineInspectorTransitionCatalogItem[] = Object.freeze<TimelineInspectorTransitionCatalogItem[]>([
  { kind: "cross-dissolve", label: "Cross dissolve", description: "Blend two clips smoothly.", defaultDurationSeconds: 0.35 },
  { kind: "fade", label: "Fade", description: "Fade between clips or to transparency.", defaultDurationSeconds: 0.3 },
  { kind: "dip-to-black", label: "Dip to black", description: "Pass through black between clips.", defaultDurationSeconds: 0.45 },
  { kind: "wipe-left", label: "Wipe left", description: "Reveal the next clip with a directional wipe.", defaultDurationSeconds: 0.4 },
  { kind: "zoom", label: "Zoom", description: "Zoom through the cut point.", defaultDurationSeconds: 0.35 },
]);

export class TimelineEffectsInspectorController {
  private selectedProperty: TimelineAnimatableProperty = "opacity";
  private interpolation: TimelineInterpolation = "ease-in-out";
  private searchQuery = "";

  getPropertyDescriptors(): readonly TimelineInspectorPropertyDescriptor[] { return PROPERTY_DESCRIPTORS; }
  getEffectCatalog(): readonly TimelineInspectorEffectCatalogItem[] { return this.filter(EFFECT_CATALOG); }
  getTransitionCatalog(): readonly TimelineInspectorTransitionCatalogItem[] { return this.filter(TRANSITION_CATALOG); }
  getSelectedProperty(): TimelineAnimatableProperty { return this.selectedProperty; }
  setSelectedProperty(property: TimelineAnimatableProperty): void { this.selectedProperty = property; }
  getInterpolation(): TimelineInterpolation { return this.interpolation; }
  setInterpolation(interpolation: TimelineInterpolation): void { this.interpolation = interpolation; }
  getSearchQuery(): string { return this.searchQuery; }
  setSearchQuery(query: string): void { this.searchQuery = query.trim().toLowerCase(); }
  clamp(property: TimelineAnimatableProperty, value: number): number {
    const descriptor = PROPERTY_DESCRIPTORS.find((item) => item.property === property);
    if (!descriptor || !Number.isFinite(value)) return descriptor?.defaultValue ?? 0;
    return Math.min(descriptor.max, Math.max(descriptor.min, value));
  }
  private filter<T extends { readonly label: string; readonly description: string }>(items: readonly T[]): readonly T[] {
    if (!this.searchQuery) return items;
    return items.filter((item) => `${item.label} ${item.description}`.toLowerCase().includes(this.searchQuery));
  }
}
