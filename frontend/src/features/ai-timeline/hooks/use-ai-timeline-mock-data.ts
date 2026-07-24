"use client";

import { useMemo, useState } from "react";

import type { AiBlock, AiTrackDefinition, AiTrackKind } from "../types";

export const AI_TRACK_DEFINITIONS: AiTrackDefinition[] = [
  { kind: "hook-detection", label: "Hook Detection", filterKey: "hook" },
  { kind: "ai-cuts", label: "AI Cuts" },
  { kind: "broll", label: "B-roll", filterKey: "broll" },
  { kind: "subtitle-highlight", label: "Subtitle Highlight", filterKey: "subtitle" },
  { kind: "zoom", label: "Zoom", filterKey: "zoom" },
  { kind: "emoji", label: "Emoji" },
  { kind: "cta", label: "CTA", filterKey: "cta" },
  { kind: "silence-removed", label: "Silence Removed", filterKey: "silence" },
  { kind: "emotion-peak", label: "Emotion Peak", filterKey: "emotion" },
  { kind: "story-beat", label: "Story Beat" },
];

export interface RealTimelineClipRef {
  id: string;
  startTime: number;
  endTime: number;
}

interface MockBlockSeed {
  trackKind: AiTrackKind;
  title: string;
  startPct: number;
  endPct: number;
  reason: string;
  confidence: number;
  extras?: Partial<AiBlock>;
}

const SEEDS: MockBlockSeed[] = [
  { trackKind: "hook-detection", title: "Opening hook", startPct: 0, endPct: 0.06, reason: "Strong pattern interrupt in first 3 seconds", confidence: 0.92, extras: { hookStrength: 0.88 } },
  { trackKind: "ai-cuts", title: "Cut — silence", startPct: 0.08, endPct: 0.09, reason: "1.4s of silence reduced pacing", confidence: 0.81, extras: { cutReason: "silence" } },
  { trackKind: "ai-cuts", title: "Cut — scene change", startPct: 0.22, endPct: 0.225, reason: "Visual scene changed abruptly", confidence: 0.74, extras: { cutReason: "scene-change" } },
  { trackKind: "ai-cuts", title: "Cut — emotion dip", startPct: 0.4, endPct: 0.41, reason: "Speech energy dropped for 2.1s", confidence: 0.68, extras: { cutReason: "emotion" } },
  { trackKind: "broll", title: "City B-roll", startPct: 0.12, endPct: 0.19, reason: "Supports the spoken sentence about urban life", confidence: 0.77, extras: { source: "stock:city-night-01" } },
  { trackKind: "broll", title: "Office B-roll", startPct: 0.5, endPct: 0.56, reason: "Illustrates the workplace example being discussed", confidence: 0.71, extras: { source: "local:broll_office.mp4" } },
  { trackKind: "subtitle-highlight", title: "Emphasis: \"never\"", startPct: 0.05, endPct: 0.07, reason: "Speech energy increased on this word", confidence: 0.85, extras: { wordEmphasis: "never", animation: "pop-scale" } },
  { trackKind: "subtitle-highlight", title: "Emphasis: \"free\"", startPct: 0.31, endPct: 0.33, reason: "Keyword aligned with CTA intent", confidence: 0.79, extras: { wordEmphasis: "free", animation: "color-flash" } },
  { trackKind: "zoom", title: "Punch-in zoom", startPct: 0.05, endPct: 0.07, reason: "Reinforces the hook's key phrase", confidence: 0.83, extras: { zoomIntensity: 0.35 } },
  { trackKind: "zoom", title: "Slow zoom", startPct: 0.6, endPct: 0.68, reason: "Builds tension before the CTA", confidence: 0.66, extras: { zoomIntensity: 0.15 } },
  { trackKind: "emoji", title: "🔥 emoji", startPct: 0.09, endPct: 0.1, reason: "Reinforces high-energy moment", confidence: 0.6 },
  { trackKind: "emoji", title: "👀 emoji", startPct: 0.34, endPct: 0.35, reason: "Draws attention to the reveal", confidence: 0.58 },
  { trackKind: "cta", title: "Follow for more", startPct: 0.92, endPct: 1, reason: "Placed after the story resolves, standard CTA position", confidence: 0.88 },
  { trackKind: "silence-removed", title: "Removed pause", startPct: 0.08, endPct: 0.081, reason: "1.4 seconds of dead air trimmed", confidence: 0.9, extras: { durationRemoved: 1.4 } },
  { trackKind: "silence-removed", title: "Removed pause", startPct: 0.44, endPct: 0.441, reason: "0.9 seconds of dead air trimmed", confidence: 0.87, extras: { durationRemoved: 0.9 } },
  { trackKind: "emotion-peak", title: "High energy", startPct: 0.02, endPct: 0.08, reason: "Vocal energy and pacing peaked", confidence: 0.8, extras: { emotionLevel: "high" } },
  { trackKind: "emotion-peak", title: "Medium energy", startPct: 0.4, endPct: 0.5, reason: "Steady, explanatory tone", confidence: 0.62, extras: { emotionLevel: "medium" } },
  { trackKind: "emotion-peak", title: "Low energy", startPct: 0.7, endPct: 0.78, reason: "Reflective, lower-energy segment", confidence: 0.55, extras: { emotionLevel: "low" } },
  { trackKind: "story-beat", title: "Hook", startPct: 0, endPct: 0.08, reason: "Opening pattern interrupt", confidence: 0.9, extras: { storyBeat: "hook" } },
  { trackKind: "story-beat", title: "Problem", startPct: 0.08, endPct: 0.35, reason: "Establishes the viewer's pain point", confidence: 0.75, extras: { storyBeat: "problem" } },
  { trackKind: "story-beat", title: "Solution", startPct: 0.35, endPct: 0.75, reason: "Presents the core solution", confidence: 0.78, extras: { storyBeat: "solution" } },
  { trackKind: "story-beat", title: "CTA", startPct: 0.75, endPct: 0.92, reason: "Calls the viewer to action", confidence: 0.83, extras: { storyBeat: "cta" } },
  { trackKind: "story-beat", title: "End", startPct: 0.92, endPct: 1, reason: "Closing frame", confidence: 0.7, extras: { storyBeat: "end" } },
];

function findOverlappingClip(
  startTime: number,
  endTime: number,
  clips: RealTimelineClipRef[],
): RealTimelineClipRef | undefined {
  const midpoint = (startTime + endTime) / 2;
  return clips.find((clip) => midpoint >= clip.startTime && midpoint <= clip.endTime);
}

function buildMockBlocks(duration: number, revision: number, realClips: RealTimelineClipRef[]): AiBlock[] {
  const safeDuration = duration > 0 ? duration : 60;

  return SEEDS.map((seed, index) => {
    const startTime = seed.startPct * safeDuration;
    const endTime = seed.endPct * safeDuration;
    const linkedClip = findOverlappingClip(startTime, endTime, realClips);

    return {
      id: `ai-block-${index}`,
      trackKind: seed.trackKind,
      title: seed.title,
      startTime,
      endTime,
      confidence: seed.confidence,
      reason: seed.reason,
      aiModel: "clip-agent-vision-1",
      generatedAt: "2026-07-20T09:41:00Z",
      promptUsed: "Analyze pacing, hooks, and emotional peaks for short-form repurposing.",
      estimatedImpact: "+12% projected retention",
      generatedAtRevision: revision,
      linkedClipId: linkedClip?.id,
      ...seed.extras,
    };
  });
}

/**
 * Mock AI-decision dataset for the AI Timeline layer. No API calls — this is
 * visualization-only per the sprint scope. `duration` should come from the
 * real timeline's view-model so blocks line up proportionally.
 *
 * Blocks are regenerated only when `duration` changes (production loaded),
 * NOT on every `revision` bump — the current `revision` is only used to stamp
 * `generatedAtRevision` the first time, which is what lets the timeline later
 * detect a block has gone stale (current revision has moved on) without
 * silently regenerating or deleting it.
 */
export function useAiTimelineMockData(
  duration: number,
  revision: number,
  realClips: RealTimelineClipRef[] = [],
): { tracks: AiTrackDefinition[]; blocks: AiBlock[] } {
  // Captures the revision current at the moment blocks are (re)generated —
  // re-captured only when `duration` changes (the React-documented "adjust
  // state when a prop changes" pattern: a conditional setState during render,
  // not inside an effect) — so later comparisons against the live `revision`
  // can tell a block has gone stale.
  const [prevDuration, setPrevDuration] = useState(duration);
  const [capturedRevision, setCapturedRevision] = useState(revision);
  if (duration !== prevDuration) {
    setPrevDuration(duration);
    setCapturedRevision(revision);
  }

  const blocks = useMemo(
    () => buildMockBlocks(duration, capturedRevision, realClips),
    // eslint-disable-next-line react-hooks/exhaustive-deps -- realClips intentionally excluded: linking happens once at generation time, not re-run on every clip edit (that's what "stale" is for).
    [duration, capturedRevision],
  );

  return useMemo(() => ({ tracks: AI_TRACK_DEFINITIONS, blocks }), [blocks]);
}
