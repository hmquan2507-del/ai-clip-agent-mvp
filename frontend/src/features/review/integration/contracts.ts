import type { ReviewBadgeTone } from "../design-system";

export type ReviewTimelineClipTone =
  | "video"
  | "broll"
  | "subtitle"
  | "audio";

export interface ReviewEditorHeaderView {
  productionId: string;
  title: string;
  durationLabel: string;
  statusLabel: string;
  statusTone: ReviewBadgeTone;
  dirty: boolean;
  canUndo: boolean;
  canRedo: boolean;
}

export interface ReviewPreviewView {
  available: boolean;
  videoUrl: string | null;
  thumbnailUrl: string | null;
  currentTime: number;
  duration: number;
  currentTimeLabel: string;
  durationLabel: string;
  headline: string;
  eyebrow: string;
  subtitle: string | null;
}

export interface ReviewTimelineClipView {
  id: string;
  label: string;
  start: number;
  width: number;
  tone: ReviewTimelineClipTone;
  selected: boolean;
}

export interface ReviewTimelineTrackView {
  id: string;
  label: string;
  trackType: string;
  locked: boolean;
  muted: boolean;
  clips: ReviewTimelineClipView[];
}

export interface ReviewTimelineView {
  duration: number;
  durationLabel: string;
  trackCount: number;
  clipCount: number;
  playheadPercent: number;
  rulerMarks: string[];
  tracks: ReviewTimelineTrackView[];
}

export interface ReviewInspectorView {
  selectedClipId: string | null;
  selectedClipLabel: string | null;
  selectedClipRange: string | null;
  positionLabel: string;
  scaleLabel: string;
  rotationLabel: string;
  opacityLabel: string;
  subtitlePreset: string;
  aiScore: number | null;
  aiSuggestion: string | null;
}

export interface ReviewEditorViewModel {
  header: ReviewEditorHeaderView;
  preview: ReviewPreviewView;
  timeline: ReviewTimelineView;
  inspector: ReviewInspectorView;
}

