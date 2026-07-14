import type {
  EditableTimelineClip,
  EditableTimelineTrack,
  JsonObject,
  JsonValue,
  ReviewRuntimeSessionSnapshot,
} from "../api";
import type { ReviewWorkspaceRuntimeState } from "../state";
import type {
  ReviewEditorViewModel,
  ReviewTimelineClipTone,
  ReviewTimelineTrackView,
} from "./contracts";

export function buildReviewEditorViewModel(
  state: ReviewWorkspaceRuntimeState,
): ReviewEditorViewModel {
  const snapshot = requireSnapshot(state.snapshot);
  const timeline = snapshot.timeline;
  const selectedIds = new Set(snapshot.selection.state.selected_clip_ids);
  const activeClip = findActiveClip(
    timeline.tracks,
    snapshot.selection.state.active_clip_id,
  );
  const duration = Math.max(0, timeline.duration);
  const currentTime = clamp(
    snapshot.preview.state.current_time,
    0,
    duration,
  );
  const title =
    readString(snapshot.workspace.metadata, "title") ??
    readString(timeline.metadata, "title") ??
    `Production ${shortId(state.productionId ?? timeline.production_id)}`;
  const aiSuggestion = firstSuggestion(snapshot.workspace.ai.suggestions);
  const aiScore = readNumber(snapshot.workspace.ai.metadata, "score");

  return {
    header: {
      productionId: state.productionId ?? timeline.production_id,
      title,
      durationLabel: formatTime(duration),
      statusLabel: timeline.dirty ? "Chưa lưu" : "Đã đồng bộ",
      statusTone: timeline.dirty ? "warning" : "success",
      dirty: timeline.dirty,
      canUndo: snapshot.history.can_undo,
      canRedo: snapshot.history.can_redo,
    },
    preview: {
      available: snapshot.preview.source.available,
      videoUrl:
        snapshot.preview.source.video_url ??
        snapshot.workspace.preview.video_url,
      thumbnailUrl: snapshot.workspace.preview.thumbnail_url,
      currentTime,
      duration,
      currentTimeLabel: formatTime(currentTime, true),
      durationLabel: formatTime(duration),
      eyebrow:
        readString(snapshot.workspace.metadata, "hook_label") ??
        "AI EDIT PREVIEW",
      headline:
        activeClip?.text ??
        readString(snapshot.workspace.metadata, "headline") ??
        title,
      subtitle:
        activeClip?.text ??
        readString(snapshot.workspace.metadata, "subtitle"),
    },
    timeline: {
      duration,
      durationLabel: formatTime(duration),
      trackCount: timeline.track_count,
      clipCount: timeline.clip_count,
      playheadPercent:
        duration > 0 ? clamp((currentTime / duration) * 100, 0, 100) : 0,
      rulerMarks: buildRulerMarks(duration),
      tracks: timeline.tracks.map((track) =>
        buildTrackView(track, duration, selectedIds),
      ),
    },
    inspector: {
      selectedClipId: activeClip?.clip_id ?? null,
      selectedClipLabel: activeClip ? clipLabel(activeClip) : null,
      selectedClipRange: activeClip
        ? `${formatTime(activeClip.start_time, true)}–${formatTime(
            activeClip.end_time,
            true,
          )}`
        : null,
      positionLabel:
        activeClip && readString(activeClip.metadata, "position")
          ? readString(activeClip.metadata, "position") ?? "X 0 · Y 0"
          : "X 0 · Y 0",
      scaleLabel:
        activeClip && readNumber(activeClip.metadata, "scale") !== null
          ? `${readNumber(activeClip.metadata, "scale")}%`
          : "100%",
      rotationLabel:
        activeClip && readNumber(activeClip.metadata, "rotation") !== null
          ? `${readNumber(activeClip.metadata, "rotation")}°`
          : "0°",
      opacityLabel:
        activeClip?.opacity !== null && activeClip?.opacity !== undefined
          ? `${Math.round(activeClip.opacity * 100)}%`
          : "100%",
      subtitlePreset:
        activeClip && readString(activeClip.metadata, "subtitle_preset")
          ? readString(activeClip.metadata, "subtitle_preset") ?? "Mặc định"
          : "Mặc định",
      aiScore,
      aiSuggestion,
    },
  };
}

function buildTrackView(
  track: EditableTimelineTrack,
  duration: number,
  selectedIds: Set<string>,
): ReviewTimelineTrackView {
  return {
    id: track.track_id,
    label: track.name?.trim() || trackTypeLabel(track.track_type),
    trackType: track.track_type,
    locked: track.locked,
    muted: track.muted,
    clips: track.clips.map((clip) => ({
      id: clip.clip_id,
      label: clipLabel(clip),
      start:
        duration > 0
          ? clamp((clip.start_time / duration) * 100, 0, 100)
          : 0,
      width:
        duration > 0
          ? clamp((clip.duration / duration) * 100, 0.5, 100)
          : 0.5,
      tone: clipTone(clip, track),
      selected: selectedIds.has(clip.clip_id),
    })),
  };
}

function clipTone(
  clip: EditableTimelineClip,
  track: EditableTimelineTrack,
): ReviewTimelineClipTone {
  const value = `${clip.clip_type}:${track.track_type}`;

  if (value.includes("subtitle")) return "subtitle";
  if (value.includes("broll") || value.includes("overlay")) return "broll";
  if (
    value.includes("music") ||
    value.includes("audio") ||
    value.includes("voice") ||
    value.includes("sound_effect")
  ) {
    return "audio";
  }

  return "video";
}

function clipLabel(clip: EditableTimelineClip): string {
  return (
    clip.text?.trim() ||
    readString(clip.metadata, "label") ||
    readString(clip.metadata, "name") ||
    clip.clip_type.replaceAll("_", " ")
  );
}

function trackTypeLabel(value: string): string {
  const labels: Record<string, string> = {
    video_primary: "Video chính",
    video_overlay: "Video phủ",
    broll: "B-roll",
    subtitle: "Phụ đề",
    music: "Nhạc nền",
    sound_effect: "Hiệu ứng âm thanh",
    voice: "Giọng nói",
    audio: "Âm thanh",
    effect: "Hiệu ứng",
  };

  return labels[value] ?? value.replaceAll("_", " ");
}

function findActiveClip(
  tracks: EditableTimelineTrack[],
  activeClipId: string | null,
): EditableTimelineClip | null {
  if (!activeClipId) return null;

  for (const track of tracks) {
    const clip = track.clips.find((item) => item.clip_id === activeClipId);
    if (clip) return clip;
  }

  return null;
}

function firstSuggestion(values: JsonValue[]): string | null {
  for (const value of values) {
    if (typeof value === "string" && value.trim()) return value.trim();
    if (isObject(value)) {
      const message = readString(value, "message") ?? readString(value, "text");
      if (message) return message;
    }
  }

  return null;
}

function buildRulerMarks(duration: number): string[] {
  const safeDuration = Math.max(duration, 1);
  return Array.from({ length: 6 }, (_, index) =>
    formatTime((safeDuration / 5) * index),
  );
}

function formatTime(value: number, precise = false): string {
  const safeValue = Math.max(0, Number.isFinite(value) ? value : 0);
  const minutes = Math.floor(safeValue / 60);
  const seconds = Math.floor(safeValue % 60);
  const base = `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(
    2,
    "0",
  )}`;

  if (!precise) return base;
  return `${base}.${Math.floor((safeValue % 1) * 100)
    .toString()
    .padStart(2, "0")}`;
}

function shortId(value: string): string {
  return value.slice(0, 8);
}

function readString(value: JsonObject, key: string): string | null {
  const candidate = value[key];
  return typeof candidate === "string" && candidate.trim()
    ? candidate.trim()
    : null;
}

function readNumber(value: JsonObject, key: string): number | null {
  const candidate = value[key];
  return typeof candidate === "number" && Number.isFinite(candidate)
    ? candidate
    : null;
}

function isObject(value: JsonValue): value is JsonObject {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function requireSnapshot(
  snapshot: ReviewRuntimeSessionSnapshot | null,
): ReviewRuntimeSessionSnapshot {
  if (!snapshot) {
    throw new Error("Review runtime snapshot is required.");
  }

  return snapshot;
}

function clamp(value: number, minimum: number, maximum: number): number {
  return Math.min(Math.max(value, minimum), maximum);
}

