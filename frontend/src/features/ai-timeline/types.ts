export type AiTrackKind =
  | "hook-detection"
  | "ai-cuts"
  | "broll"
  | "subtitle-highlight"
  | "zoom"
  | "emoji"
  | "cta"
  | "silence-removed"
  | "emotion-peak"
  | "story-beat";

export type AiTrackVisibility = "shown" | "hidden";

export interface AiTrackState {
  visibility: AiTrackVisibility;
  locked: boolean;
  muted: boolean;
  collapsed: boolean;
}

export interface AiTrackDefinition {
  kind: AiTrackKind;
  label: string;
  /** Category used by the toolbar's quick filters (a subset of tracks are filterable). */
  filterKey?: AiFilterKey;
}

export type AiFilterKey = "hook" | "subtitle" | "broll" | "cta" | "emotion" | "zoom" | "silence";

export type AiCutReason =
  | "silence"
  | "emotion"
  | "scene-change"
  | "hook"
  | "cta"
  | "visual-interest";

export type AiEmotionLevel = "high" | "medium" | "low";

export type AiStoryBeat = "hook" | "problem" | "solution" | "cta" | "end";

/**
 * A single AI decision rendered as one block on the AI Timeline. This is a
 * pure UI/visualization model — it does not read from or write to the
 * Timeline/Playback/AI runtimes. `linkedClipId` is an optional pointer a
 * future integration could use to cross-highlight the real timeline clip;
 * this sprint only renders the block and exposes callbacks.
 */
export interface AiBlock {
  id: string;
  trackKind: AiTrackKind;
  title: string;
  startTime: number;
  endTime: number;
  confidence: number; // 0..1
  reason: string;
  source?: string;
  aiModel: string;
  generatedAt: string;
  promptUsed?: string;
  estimatedImpact?: string;
  linkedClipId?: string;
  pinned?: boolean;
  disabled?: boolean;
  manual?: boolean;
  status?: AiBlockStatus;
  /** The real timeline revision that was current when this decision was generated — compared live against the current revision to derive "stale". */
  generatedAtRevision?: number;

  // Track-kind-specific extras (all optional; presence depends on trackKind).
  cutReason?: AiCutReason;
  emotionLevel?: AiEmotionLevel;
  storyBeat?: AiStoryBeat;
  wordEmphasis?: string;
  animation?: string;
  zoomIntensity?: number;
  durationRemoved?: number;
  hookStrength?: number;
}

export type AiBlockStatus = "idle" | "processing" | "regenerating";

/**
 * The single, mutually-exclusive visual treatment for a block, derived (not
 * stored) from its live state each render. Priority order matches the list
 * order below — e.g. a processing block always reads as "processing" even if
 * it's also pinned.
 */
export type AiBlockVisualState =
  | "processing"
  | "regenerating"
  | "disabled"
  | "stale"
  | "selected"
  | "hovered"
  | "pinned"
  | "normal";

export interface AiBlockVisualStateInput {
  status?: AiBlockStatus;
  disabled?: boolean;
  stale: boolean;
  selected: boolean;
  hovered: boolean;
  pinned?: boolean;
}

export function resolveAiBlockVisualState(input: AiBlockVisualStateInput): AiBlockVisualState {
  if (input.status === "processing") return "processing";
  if (input.status === "regenerating") return "regenerating";
  if (input.disabled) return "disabled";
  if (input.stale) return "stale";
  if (input.selected) return "selected";
  if (input.hovered) return "hovered";
  if (input.pinned) return "pinned";
  return "normal";
}

export type AiBlockAction =
  | "regenerate"
  | "disable"
  | "duplicate"
  | "convert-to-manual"
  | "delete"
  | "pin"
  | "explain";

export interface AiBlockActionIntent {
  action: AiBlockAction;
  block: AiBlock;
}
