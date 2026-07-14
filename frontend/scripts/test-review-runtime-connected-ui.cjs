/* eslint-disable @typescript-eslint/no-require-imports */

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const React = require("react");
const { renderToStaticMarkup } = require("react-dom/server");
const ts = require("typescript");

function compileTypeScript(module, filename) {
  const source = fs.readFileSync(filename, "utf8");
  const output = ts.transpileModule(source, {
    fileName: filename,
    compilerOptions: {
      target: ts.ScriptTarget.ES2022,
      module: ts.ModuleKind.CommonJS,
      moduleResolution: ts.ModuleResolutionKind.NodeJs,
      jsx: ts.JsxEmit.ReactJSX,
      esModuleInterop: true,
    },
  });

  module._compile(output.outputText, filename);
}

require.extensions[".ts"] = compileTypeScript;
require.extensions[".tsx"] = compileTypeScript;

const {
  ReviewRuntimeWorkspace,
  buildReviewEditorViewModel,
} = require(path.resolve(
  __dirname,
  "../src/features/review/integration/index.ts",
));
const { ReviewEditorShell } = require(path.resolve(
  __dirname,
  "../src/features/review/shell/index.ts",
));

const productionId = "221e4b01-5fb9-4b4a-a549-4fb32c455059";
const sessionId = "session-runtime-ui";

function clip(id, trackId, start, end, type, text = null) {
  return {
    clip_id: id,
    track_id: trackId,
    clip_type: type,
    start_time: start,
    end_time: end,
    duration: end - start,
    source_start: 0,
    source_end: end - start,
    source_duration: end - start,
    source_range_duration: end - start,
    asset_id: null,
    local_path: null,
    text,
    volume: 1,
    opacity: 0.8,
    speed: 1,
    enabled: true,
    metadata: { label: text ?? id, scale: 110, rotation: 2 },
  };
}

function buildState() {
  const session = {
    session_id: sessionId,
    production_id: productionId,
    status: "ready",
    active: true,
    ready: true,
    closed: false,
    timeline_revision: 4,
    dirty: true,
    revision: 4,
    created_at: "2026-07-14T00:00:00.000Z",
    updated_at: "2026-07-14T00:00:01.000Z",
    closed_at: null,
    error: null,
    metadata: {},
  };
  const videoClip = clip("clip-video", "track-video", 0, 12, "video");
  const subtitleClip = clip(
    "clip-subtitle",
    "track-subtitle",
    2,
    8,
    "subtitle",
    "Hook runtime thật",
  );
  const tracks = [
    {
      track_id: "track-video",
      track_type: "video_primary",
      name: "Video chính",
      position: 0,
      layer: 0,
      locked: false,
      muted: false,
      hidden: false,
      enabled: true,
      overlap_policy: "forbid",
      clip_count: 1,
      clips: [videoClip],
      metadata: {},
    },
    {
      track_id: "track-subtitle",
      track_type: "subtitle",
      name: "Phụ đề",
      position: 1,
      layer: 1,
      locked: false,
      muted: false,
      hidden: false,
      enabled: true,
      overlap_policy: "allow",
      clip_count: 1,
      clips: [subtitleClip],
      metadata: {},
    },
  ];
  const timeline = {
    production_id: productionId,
    version: "16.3.6",
    duration: 20,
    fps: 30,
    minimum_clip_duration: 1 / 30,
    width: 1080,
    height: 1920,
    track_count: 2,
    clip_count: 2,
    revision: 4,
    dirty: true,
    dirty_status: "dirty",
    created_at: "2026-07-14T00:00:00.000Z",
    updated_at: "2026-07-14T00:00:01.000Z",
    tracks,
    metadata: { title: "Runtime Video" },
  };

  return {
    status: "ready",
    pendingOperation: null,
    productionId,
    sessionId,
    session,
    error: null,
    requestRevision: 1,
    stateRevision: 2,
    updatedAt: "2026-07-14T00:00:01.000Z",
    snapshot: {
      session,
      workspace: {
        production_id: productionId,
        version: "16.3.6",
        preview: {
          available: true,
          video_url: "https://example.test/preview.mp4",
          thumbnail_url: "https://example.test/preview.jpg",
          duration: 20,
          width: 1080,
          height: 1920,
          fps: 30,
        },
        timeline: {
          version: "16.3.6",
          duration: 20,
          track_count: 2,
          clip_count: 2,
          tracks,
        },
        review: { is_approved: false, notes: null },
        export: { is_exported: false, export_url: null, export_format: null },
        ai: {
          suggestions: [{ message: "Tăng tốc hook thêm 8%." }],
          metadata: { score: 94 },
        },
        selection: { selected_clip_ids: ["clip-subtitle"] },
        metadata: { title: "Runtime Video", hook_label: "HOOK TỪ BACKEND" },
      },
      timeline,
      preview: {
        source: {
          production_id: productionId,
          video_path: null,
          video_url: "https://example.test/preview.mp4",
          available: true,
          duration: 20,
          width: 1080,
          height: 1920,
          fps: 30,
          frame_duration: 1 / 30,
          total_frames: 600,
          metadata: {},
        },
        state: {
          production_id: productionId,
          status: "paused",
          playing: false,
          current_time: 5,
          duration: 20,
          progress: 0.25,
          volume: 1,
          muted: false,
          effective_volume: 1,
          playback_rate: 1,
          zoom: 1,
          loop_enabled: false,
          current_frame: 150,
          total_frames: 600,
          revision: 1,
          created_at: "2026-07-14T00:00:00.000Z",
          updated_at: "2026-07-14T00:00:01.000Z",
          error: null,
          metadata: {},
        },
        sync: {
          production_id: productionId,
          status: "current",
          available: true,
          current: true,
          stale: false,
          active_timeline_revision: 4,
          preview_timeline_revision: 4,
          reason: null,
          updated_at: "2026-07-14T00:00:01.000Z",
          metadata: {},
        },
      },
      selection: {
        catalog: {
          production_id: productionId,
          duration: 20,
          fps: 30,
          track_count: 2,
          clip_count: 2,
          tracks: [],
          clips: [],
          metadata: {},
        },
        state: {
          production_id: productionId,
          mode: "single",
          focus: "clip",
          selected_track_ids: ["track-subtitle"],
          selected_clip_ids: ["clip-subtitle"],
          active_track_id: "track-subtitle",
          active_clip_id: "clip-subtitle",
          hovered_track_id: null,
          hovered_clip_id: null,
          cursor_time: 5,
          cursor_frame: 150,
          selected_range: null,
          has_selection: true,
          selected_count: 1,
          revision: 2,
          created_at: "2026-07-14T00:00:00.000Z",
          updated_at: "2026-07-14T00:00:01.000Z",
          metadata: {},
        },
      },
      history: {
        production_id: productionId,
        can_undo: true,
        can_redo: false,
        undo_count: 2,
        redo_count: 0,
        current_revision: 4,
        maximum_history_size: 100,
        next_undo_label: "Di chuyển clip",
        next_redo_label: null,
      },
      clipboard: {
        state: {
          production_id: productionId,
          status: "empty",
          available: false,
          item_count: 0,
          clip_count: 0,
          clipboard_id: "",
          last_action: null,
          source_track_ids: [],
        },
        content: {
          clipboard_id: "",
          production_id: productionId,
          action: "clear",
          status: "empty",
          available: false,
          item_count: 0,
          clip_count: 0,
          source_track_ids: [],
          anchor_time: 0,
          total_duration: 0,
          created_at: "2026-07-14T00:00:00.000Z",
          items: [],
          metadata: {},
        },
      },
      created_at: "2026-07-14T00:00:01.000Z",
      consistency: {
        production_ids_match: true,
        workspace_timeline_consistent: true,
      },
      metadata: {},
    },
  };
}

function main() {
  const state = buildState();
  const view = buildReviewEditorViewModel(state);
  const html = renderToStaticMarkup(
    React.createElement(ReviewEditorShell, { view }),
  );
  const loadingHtml = renderToStaticMarkup(
    React.createElement(ReviewRuntimeWorkspace, { productionId }),
  );

  const checks = {
    runtime_title_mapped: view.header.title === "Runtime Video",
    runtime_status_mapped:
      view.header.dirty === true && view.header.statusLabel === "Chưa lưu",
    preview_source_mapped:
      view.preview.videoUrl === "https://example.test/preview.mp4" &&
      view.preview.currentTimeLabel === "00:05.00",
    timeline_mapped:
      view.timeline.trackCount === 2 &&
      view.timeline.clipCount === 2 &&
      view.timeline.playheadPercent === 25,
    clip_geometry_mapped:
      view.timeline.tracks[0].clips[0].start === 0 &&
      view.timeline.tracks[0].clips[0].width === 60,
    selection_mapped:
      view.timeline.tracks[1].clips[0].selected === true &&
      view.inspector.selectedClipId === "clip-subtitle",
    ai_suggestion_mapped:
      view.inspector.aiScore === 94 &&
      view.inspector.aiSuggestion === "Tăng tốc hook thêm 8%.",
    runtime_shell_rendered:
      html.includes("Runtime Video") &&
      html.includes("Hook runtime thật") &&
      html.includes("https://example.test/preview.mp4"),
    ai_command_safely_disabled: html.includes('disabled=""'),
    provider_initial_loading: loadingHtml.includes("Đang mở AI Video Editor"),
    source_state_unchanged: state.snapshot.timeline.revision === 4,
  };

  console.log("=== Runtime-connected Review UI ===");

  for (const [name, value] of Object.entries(checks)) {
    console.log(`${name}: ${value}`);
    assert.equal(value, true, `${name} failed`);
  }

  console.log("\nDONE: Runtime-connected Review UI test completed.");
}

main();

