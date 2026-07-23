import type { TimelineAnimatableProperty, TimelineEffectKind, TimelineInterpolation, TimelineTransitionKind } from "./timeline-effects-animation-contracts";

export const TIMELINE_EFFECTS_INSPECTOR_CONTRACT_VERSION = 1 as const;

export interface TimelineInspectorPropertyDescriptor {
  readonly property: TimelineAnimatableProperty;
  readonly label: string;
  readonly min: number;
  readonly max: number;
  readonly step: number;
  readonly defaultValue: number;
  readonly unit?: string;
}

export interface TimelineInspectorEffectCatalogItem {
  readonly kind: TimelineEffectKind;
  readonly label: string;
  readonly description: string;
  readonly defaultParameters: Readonly<Record<string, number>>;
}

export interface TimelineInspectorTransitionCatalogItem {
  readonly kind: TimelineTransitionKind;
  readonly label: string;
  readonly description: string;
  readonly defaultDurationSeconds: number;
}

export interface TimelineEffectsInspectorPreferences {
  readonly expandedSections: readonly string[];
  readonly selectedProperty: TimelineAnimatableProperty;
  readonly interpolation: TimelineInterpolation;
  readonly searchQuery: string;
}
