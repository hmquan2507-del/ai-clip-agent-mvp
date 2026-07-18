import type {
  EditableTimelineClip,
  EditableTimelineTrack,
  JsonObject,
  JsonValue,
  ReviewRuntimeSessionSnapshot,
} from "../api";

import type {
  ReviewWorkspaceRuntimeState,
} from "../state";

import type {
  ReviewEditorViewModel,
  ReviewTimelineClipTone,
  ReviewTimelineCommandTargetView,
  ReviewTimelineTrackView,
} from "./contracts";

interface ActiveClipContext {
  clip: EditableTimelineClip;
  track: EditableTimelineTrack;
}

export function buildReviewEditorViewModel(
  state: ReviewWorkspaceRuntimeState,
): ReviewEditorViewModel {
  const snapshot =
    requireSnapshot(
      state.snapshot,
    );

  const timeline =
    snapshot.timeline;

  const selection =
    snapshot.selection.state;

  const selectedIds =
    new Set(
      selection.selected_clip_ids,
    );

  const activeContext =
    findActiveClipContext(
      timeline.tracks,
      selection.active_clip_id,
    );

  const activeClip =
    activeContext?.clip ?? null;

  const duration =
    Math.max(
      0,
      timeline.duration,
    );

  const currentTime =
    clamp(
      snapshot.preview.state
        .current_time,
      0,
      duration,
    );

  const title =
    readString(
      snapshot.workspace.metadata,
      "title",
    ) ??
    readString(
      timeline.metadata,
      "title",
    ) ??
    `Production ${shortId(
      state.productionId ??
        timeline.production_id,
    )}`;

  const aiSuggestion =
    firstSuggestion(
      snapshot.workspace.ai
        .suggestions,
    );

  const aiScore =
    readNumber(
      snapshot.workspace.ai
        .metadata,
      "score",
    );

  const commandTarget =
    buildCommandTarget(
      activeContext,
      selection.cursor_time,
      timeline.minimum_clip_duration,
    );

  const selectedClipIds =
    selection.selected_clip_ids.filter(
      (clipId) =>
        findActiveClipContext(
          timeline.tracks,
          clipId,
        ) !== null,
    );

  const selectedTracksEditable =
    selectedClipIds.every(
      (clipId) =>
        !findActiveClipContext(
          timeline.tracks,
          clipId,
        )?.track.locked,
    );

  const clipboardState =
    snapshot.clipboard.state;

  const clipboardHistory =
    state.lastClipboardResponse
      ?.clipboard.history_state ??
    null;

  return {
    header: {
      productionId:
        state.productionId ??
        timeline.production_id,

      title,

      durationLabel:
        formatTime(duration),

      statusLabel:
        timeline.dirty
          ? "Chưa lưu"
          : "Đã đồng bộ",

      statusTone:
        timeline.dirty
          ? "warning"
          : "success",

      dirty:
        timeline.dirty,

      canUndo:
        snapshot.history.can_undo,

      canRedo:
        snapshot.history.can_redo,
    },

    preview: {
      available:
        snapshot.preview.source
          .available,

      videoUrl:
        snapshot.preview.source
          .video_url ??
        snapshot.workspace.preview
          .video_url,

      thumbnailUrl:
        snapshot.workspace.preview
          .thumbnail_url,

      currentTime,
      duration,

      currentTimeLabel:
        formatTime(
          currentTime,
          true,
        ),

      durationLabel:
        formatTime(duration),

      eyebrow:
        readString(
          snapshot.workspace.metadata,
          "hook_label",
        ) ??
        "AI EDIT PREVIEW",

      headline:
        activeClip?.text ??
        readString(
          snapshot.workspace.metadata,
          "headline",
        ) ??
        title,

      subtitle:
        activeClip?.text ??
        readString(
          snapshot.workspace.metadata,
          "subtitle",
        ),
    },

    timeline: {
      duration,

      durationLabel:
        formatTime(duration),

      trackCount:
        timeline.track_count,

      clipCount:
        timeline.clip_count,

      playheadPercent:
        duration > 0
          ? clamp(
              (
                currentTime /
                duration
              ) * 100,
              0,
              100,
            )
          : 0,

      rulerMarks:
        buildRulerMarks(
          duration,
        ),

      tracks:
        timeline.tracks.map(
          (track) =>
            buildTrackView(
              track,
              duration,
              selectedIds,
            ),
        ),

      commandTarget,

      clipboard: {
        selectedClipIds:
          [...selectedClipIds],

        pasteTime:
          clamp(
            selection.cursor_time,
            0,
            duration,
          ),

        available:
          clipboardState.available,

        itemCount:
          clipboardState.item_count,

        historyEntryCount:
          clipboardHistory?.entry_count ??
          0,

        latestHistoryEntryId:
          clipboardHistory
            ?.latest_entry_id ??
          null,

        canCopy:
          selectedClipIds.length > 0,

        canCut:
          selectedClipIds.length > 0 &&
          selectedTracksEditable,

        canPaste:
          clipboardState.available,

        canClear:
          clipboardState.available,

        canRestoreHistory:
          Boolean(
            clipboardHistory
              ?.latest_entry_id,
          ),

        canClearHistory:
          (
            clipboardHistory
              ?.entry_count ?? 0
          ) > 0,
      },
    },

    inspector: {
      selectedClipId:
        activeClip?.clip_id ??
        null,

      selectedClipLabel:
        activeClip
          ? clipLabel(activeClip)
          : null,

      selectedClipRange:
        activeClip
          ? `${formatTime(
              activeClip.start_time,
              true,
            )}–${formatTime(
              activeClip.end_time,
              true,
            )}`
          : null,

      positionLabel:
        activeClip &&
        readString(
          activeClip.metadata,
          "position",
        )
          ? readString(
              activeClip.metadata,
              "position",
            ) ?? "X 0 · Y 0"
          : "X 0 · Y 0",

      scaleLabel:
        activeClip &&
        readNumber(
          activeClip.metadata,
          "scale",
        ) !== null
          ? `${readNumber(
              activeClip.metadata,
              "scale",
            )}%`
          : "100%",

      rotationLabel:
        activeClip &&
        readNumber(
          activeClip.metadata,
          "rotation",
        ) !== null
          ? `${readNumber(
              activeClip.metadata,
              "rotation",
            )}°`
          : "0°",

      opacityLabel:
        activeClip?.opacity !==
          null &&
        activeClip?.opacity !==
          undefined
          ? `${Math.round(
              activeClip.opacity *
                100,
            )}%`
          : "100%",

      subtitlePreset:
        activeClip &&
        readString(
          activeClip.metadata,
          "subtitle_preset",
        )
          ? readString(
              activeClip.metadata,
              "subtitle_preset",
            ) ?? "Mặc định"
          : "Mặc định",

      aiScore,
      aiSuggestion,
    },
  };
}

function buildCommandTarget(
  context:
    ActiveClipContext | null,
  cursorTime: number,
  minimumClipDuration: number,
): ReviewTimelineCommandTargetView | null {
  if (!context) {
    return null;
  }

  const {
    clip,
    track,
  } = context;

  const minimumDuration =
    Number.isFinite(
      minimumClipDuration,
    ) &&
    minimumClipDuration > 0
      ? minimumClipDuration
      : 1 / 30;

  const minimumSplitTime =
    clip.start_time +
    minimumDuration;

  const maximumSplitTime =
    clip.end_time -
    minimumDuration;

  const canSplit =
    !track.locked &&
    minimumSplitTime <=
      maximumSplitTime;

  let splitTime:
    number | null = null;

  if (canSplit) {
    if (
      cursorTime >=
        minimumSplitTime &&
      cursorTime <=
        maximumSplitTime
    ) {
      splitTime =
        cursorTime;
    } else {
      splitTime =
        clip.start_time +
        clip.duration / 2;
    }
  }

  return {
    clipId:
      clip.clip_id,

    editable:
      !track.locked,

    canSplit,

    splitTime,

    gapBefore:
      track.locked
        ? null
        : findGapBeforeClip(
            track,
            clip,
          ),
  };
}

function findGapBeforeClip(
  track: EditableTimelineTrack,
  activeClip: EditableTimelineClip,
) {
  const tolerance = 0.000001;

  const previousEnd =
    track.clips
      .filter(
        (clip) =>
          clip.clip_id !==
            activeClip.clip_id &&
          clip.end_time <=
            activeClip.start_time +
              tolerance,
      )
      .reduce(
        (latest, clip) =>
          Math.max(
            latest,
            clip.end_time,
          ),
        0,
      );

  if (
    activeClip.start_time -
      previousEnd <=
    tolerance
  ) {
    return null;
  }

  return {
    trackId:
      track.track_id,

    startTime:
      previousEnd,

    endTime:
      activeClip.start_time,
  };
}

function buildTrackView(
  track: EditableTimelineTrack,
  duration: number,
  selectedIds: Set<string>,
): ReviewTimelineTrackView {
  return {
    id: track.track_id,

    label:
      track.name?.trim() ||
      trackTypeLabel(
        track.track_type,
      ),

    trackType:
      track.track_type,

    locked:
      track.locked,

    muted:
      track.muted,

    clips:
      track.clips.map(
        (clip) => ({
          id: clip.clip_id,

          label:
            clipLabel(clip),

          start:
            duration > 0
              ? clamp(
                  (
                    clip.start_time /
                    duration
                  ) * 100,
                  0,
                  100,
                )
              : 0,

          width:
            duration > 0
              ? clamp(
                  (
                    clip.duration /
                    duration
                  ) * 100,
                  0.5,
                  100,
                )
              : 0.5,

          tone:
            clipTone(
              clip,
              track,
            ),

          selected:
            selectedIds.has(
              clip.clip_id,
            ),
        }),
      ),
  };
}

function clipTone(
  clip: EditableTimelineClip,
  track: EditableTimelineTrack,
): ReviewTimelineClipTone {
  const value =
    `${clip.clip_type}:` +
    `${track.track_type}`;

  if (
    value.includes("subtitle")
  ) {
    return "subtitle";
  }

  if (
    value.includes("broll") ||
    value.includes("overlay")
  ) {
    return "broll";
  }

  if (
    value.includes("music") ||
    value.includes("audio") ||
    value.includes("voice") ||
    value.includes(
      "sound_effect",
    )
  ) {
    return "audio";
  }

  return "video";
}

function clipLabel(
  clip: EditableTimelineClip,
): string {
  return (
    clip.text?.trim() ||
    readString(
      clip.metadata,
      "label",
    ) ||
    readString(
      clip.metadata,
      "name",
    ) ||
    clip.clip_type.replaceAll(
      "_",
      " ",
    )
  );
}

function trackTypeLabel(
  value: string,
): string {
  const labels:
    Record<string, string> = {
      video_primary:
        "Video chính",
      video_overlay:
        "Video phủ",
      broll:
        "B-roll",
      subtitle:
        "Phụ đề",
      music:
        "Nhạc nền",
      sound_effect:
        "Hiệu ứng âm thanh",
      voice:
        "Giọng nói",
      audio:
        "Âm thanh",
      effect:
        "Hiệu ứng",
    };

  return (
    labels[value] ??
    value.replaceAll(
      "_",
      " ",
    )
  );
}

function findActiveClipContext(
  tracks:
    EditableTimelineTrack[],
  activeClipId:
    string | null,
): ActiveClipContext | null {
  if (!activeClipId) {
    return null;
  }

  for (
    const track
    of tracks
  ) {
    const clip =
      track.clips.find(
        (item) =>
          item.clip_id ===
          activeClipId,
      );

    if (clip) {
      return {
        clip,
        track,
      };
    }
  }

  return null;
}

function firstSuggestion(
  values: JsonValue[],
): string | null {
  for (
    const value
    of values
  ) {
    if (
      typeof value ===
        "string" &&
      value.trim()
    ) {
      return value.trim();
    }

    if (isObject(value)) {
      const message =
        readString(
          value,
          "message",
        ) ??
        readString(
          value,
          "text",
        );

      if (message) {
        return message;
      }
    }
  }

  return null;
}

function buildRulerMarks(
  duration: number,
): string[] {
  const safeDuration =
    Math.max(
      duration,
      1,
    );

  return Array.from(
    {
      length: 6,
    },
    (_, index) =>
      formatTime(
        (
          safeDuration /
          5
        ) * index,
      ),
  );
}

function formatTime(
  value: number,
  precise = false,
): string {
  const safeValue =
    Math.max(
      0,
      Number.isFinite(value)
        ? value
        : 0,
    );

  const minutes =
    Math.floor(
      safeValue / 60,
    );

  const seconds =
    Math.floor(
      safeValue % 60,
    );

  const base =
    `${String(minutes).padStart(
      2,
      "0",
    )}:` +
    `${String(seconds).padStart(
      2,
      "0",
    )}`;

  if (!precise) {
    return base;
  }

  return (
    `${base}.` +
    `${Math.floor(
      (
        safeValue %
        1
      ) * 100,
    )
      .toString()
      .padStart(
        2,
        "0",
      )}`
  );
}

function shortId(
  value: string,
): string {
  return value.slice(
    0,
    8,
  );
}

function readString(
  value: JsonObject,
  key: string,
): string | null {
  const candidate =
    value[key];

  return (
    typeof candidate ===
      "string" &&
    candidate.trim()
      ? candidate.trim()
      : null
  );
}

function readNumber(
  value: JsonObject,
  key: string,
): number | null {
  const candidate =
    value[key];

  return (
    typeof candidate ===
      "number" &&
    Number.isFinite(candidate)
      ? candidate
      : null
  );
}

function isObject(
  value: JsonValue,
): value is JsonObject {
  return (
    typeof value ===
      "object" &&
    value !== null &&
    !Array.isArray(value)
  );
}

function requireSnapshot(
  snapshot:
    ReviewRuntimeSessionSnapshot | null,
): ReviewRuntimeSessionSnapshot {
  if (!snapshot) {
    throw new Error(
      "Review runtime snapshot is required.",
    );
  }

  return snapshot;
}

function clamp(
  value: number,
  minimum: number,
  maximum: number,
): number {
  return Math.min(
    Math.max(
      value,
      minimum,
    ),
    maximum,
  );
}
