/* eslint-disable @typescript-eslint/no-require-imports */

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const ts = require("typescript");

require.extensions[".ts"] =
  function compileTypeScript(
    module,
    filename,
  ) {
    const source = fs.readFileSync(
      filename,
      "utf8",
    );

    const output = ts.transpileModule(
      source,
      {
        fileName: filename,
        compilerOptions: {
          target:
            ts.ScriptTarget.ES2022,
          module:
            ts.ModuleKind.CommonJS,
          moduleResolution:
            ts.ModuleResolutionKind.NodeJs,
          esModuleInterop: true,
        },
      },
    );

    module._compile(
      output.outputText,
      filename,
    );
  };

const {
  createReviewWorkspaceClient,
  ReviewWorkspaceAPIError,
} = require(path.resolve(
  __dirname,
  "../src/features/review/api/index.ts",
));

const {
  createReviewWorkspaceSessionRuntime,
} = require(path.resolve(
  __dirname,
  "../src/features/review/state/index.ts",
));

const productionId =
  "221e4b01-5fb9-4b4a-a549-4fb32c455059";

const sessionId =
  "review-session-selection-1";

const primaryClipId = "clip-primary-1";
const secondaryClipId = "clip-secondary-1";

function sessionState(
  timelineRevision = 3,
  sessionRevision = 1,
) {
  return {
    session_id: sessionId,
    production_id: productionId,
    status: "ready",
    active: true,
    ready: true,
    closed: false,
    timeline_revision:
      timelineRevision,
    dirty: timelineRevision > 1,
    revision: sessionRevision,
    created_at:
      "2026-07-15T00:00:00.000Z",
    updated_at:
      "2026-07-15T00:00:00.000Z",
    closed_at: null,
    error: null,
    metadata: {},
  };
}

function selectionState(
  selectedClipIds = [],
  revision = 1,
) {
  const activeClipId =
    selectedClipIds.length > 0
      ? selectedClipIds[
          selectedClipIds.length - 1
        ]
      : null;

  return {
    production_id: productionId,
    mode:
      selectedClipIds.length > 1
        ? "multi"
        : selectedClipIds.length === 1
          ? "single"
          : "none",
    focus:
      selectedClipIds.length > 0
        ? "clip"
        : "none",
    selected_track_ids:
      selectedClipIds.length > 0
        ? ["video-primary"]
        : [],
    selected_clip_ids:
      [...selectedClipIds],
    active_track_id:
      selectedClipIds.length > 0
        ? "video-primary"
        : null,
    active_clip_id: activeClipId,
    hovered_track_id: null,
    hovered_clip_id: null,
    cursor_time: 0,
    cursor_frame: 0,
    selected_range: null,
    has_selection:
      selectedClipIds.length > 0,
    selected_count:
      selectedClipIds.length,
    revision,
    created_at:
      "2026-07-15T00:00:00.000Z",
    updated_at:
      "2026-07-15T00:00:00.000Z",
    metadata: {},
  };
}

function timelineClip(
  clipId,
  startTime,
  endTime,
) {
  return {
    clip_id: clipId,
    track_id: "video-primary",
    clip_type: "video",
    start_time: startTime,
    end_time: endTime,
    duration:
      endTime - startTime,
    source_start: startTime,
    source_end: endTime,
    source_duration: 10,
    source_range_duration:
      endTime - startTime,
    asset_id: `asset-${clipId}`,
    local_path: null,
    text: null,
    volume: 1,
    opacity: 1,
    speed: 1,
    enabled: true,
    metadata: {},
  };
}

function snapshot(
  timelineRevision = 3,
  selectedClipIds = [],
  selectionRevision = 1,
  sessionRevision = 1,
) {
  const clips = [
    timelineClip(
      primaryClipId,
      0,
      4,
    ),
    timelineClip(
      secondaryClipId,
      4,
      8,
    ),
  ];

  const track = {
    track_id: "video-primary",
    track_type: "video_primary",
    name: "Video chính",
    position: 0,
    layer: 0,
    locked: false,
    muted: false,
    hidden: false,
    enabled: true,
    overlap_policy: "forbid",
    clip_count: clips.length,
    clips,
    metadata: {},
  };

  return {
    session: sessionState(
      timelineRevision,
      sessionRevision,
    ),

    workspace: {
      production_id: productionId,
      version: "16.4.7.2",

      preview: {
        available: true,
        video_url: null,
        thumbnail_url: null,
        duration: 8,
        width: 1080,
        height: 1920,
        fps: 30,
      },

      timeline: {
        version: "16.4.7.2",
        duration: 8,
        track_count: 1,
        clip_count: 2,
        tracks: [track],
      },

      review: {
        is_approved: false,
        notes: null,
      },

      export: {
        is_exported: false,
        export_url: null,
        export_format: null,
      },

      ai: {
        suggestions: [],
        metadata: {},
      },

      selection: {
        selected_clip_ids:
          [...selectedClipIds],
      },

      metadata: {},
    },

    timeline: {
      production_id: productionId,
      version: "16.4.7.2",
      duration: 8,
      fps: 30,
      minimum_clip_duration:
        1 / 30,
      width: 1080,
      height: 1920,
      track_count: 1,
      clip_count: 2,
      revision:
        timelineRevision,
      dirty:
        timelineRevision > 1,
      dirty_status:
        timelineRevision > 1
          ? "dirty"
          : "clean",
      created_at:
        "2026-07-15T00:00:00.000Z",
      updated_at:
        "2026-07-15T00:00:00.000Z",
      tracks: [track],
      metadata: {
        timeline_marker:
          `timeline-${timelineRevision}`,
      },
    },

    preview: {
      source: {
        production_id:
          productionId,
        video_path: null,
        video_url: null,
        available: false,
        duration: 8,
        width: 1080,
        height: 1920,
        fps: 30,
        frame_duration: 1 / 30,
        total_frames: 240,
        metadata: {},
      },

      state: {
        production_id:
          productionId,
        status: "ready",
        playing: false,
        current_time: 0,
        duration: 8,
        progress: 0,
        volume: 1,
        muted: false,
        effective_volume: 1,
        playback_rate: 1,
        zoom: 1,
        loop_enabled: false,
        current_frame: 0,
        total_frames: 240,
        revision: 1,
        created_at:
          "2026-07-15T00:00:00.000Z",
        updated_at:
          "2026-07-15T00:00:00.000Z",
        error: null,
        metadata: {},
      },

      sync: {
        production_id:
          productionId,
        status: "current",
        available: true,
        current: true,
        stale: false,
        active_timeline_revision:
          timelineRevision,
        preview_timeline_revision:
          timelineRevision,
        reason: null,
        updated_at:
          "2026-07-15T00:00:00.000Z",
        metadata: {},
      },
    },

    selection: {
      catalog: {
        production_id:
          productionId,
        duration: 8,
        fps: 30,
        track_count: 1,
        clip_count: 2,
        tracks: [
          {
            track_id:
              "video-primary",
            track_type:
              "video_primary",
            name: "Video chính",
            position: 0,
            clip_ids: [
              primaryClipId,
              secondaryClipId,
            ],
            metadata: {},
          },
        ],
        clips: clips.map((clip) => ({
          clip_id: clip.clip_id,
          track_id:
            clip.track_id,
          clip_type:
            clip.clip_type,
          start_time:
            clip.start_time,
          end_time:
            clip.end_time,
          duration:
            clip.duration,
          metadata: {},
        })),
        metadata: {},
      },

      state: selectionState(
        selectedClipIds,
        selectionRevision,
      ),
    },

    history: {
      production_id:
        productionId,
      can_undo: true,
      can_redo: false,
      undo_count: 2,
      redo_count: 0,
      current_revision:
        timelineRevision,
      maximum_history_size: 100,
      next_undo_label:
        "Hoàn tác thao tác trước",
      next_redo_label: null,
    },

    clipboard: {
      state: {
        production_id:
          productionId,
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
        production_id:
          productionId,
        action: "clear",
        status: "empty",
        available: false,
        item_count: 0,
        clip_count: 0,
        source_track_ids: [],
        anchor_time: 0,
        total_duration: 0,
        created_at:
          "2026-07-15T00:00:00.000Z",
        items: [],
        metadata: {},
      },
    },

    created_at:
      "2026-07-15T00:00:00.000Z",

    consistency: {
      production_ids_match: true,
      workspace_timeline_consistent:
        true,
    },

    metadata: {},
  };
}

function workspaceResponse(
  operation,
  currentSnapshot,
) {
  return {
    contract_version: "16.2.3",
    success: true,
    operation,
    production_id: productionId,
    session_id: sessionId,
    snapshot: currentSnapshot,
    metadata: {},
  };
}

function openResponse(
  currentSnapshot,
) {
  return {
    contract_version: "16.2.3",
    success: true,
    operation: "open_session",
    production_id: productionId,
    session_id: sessionId,
    session:
      currentSnapshot.session,
    snapshot:
      currentSnapshot,
    metadata: {},
  };
}

function jsonResponse(
  payload,
  status = 200,
) {
  return new Response(
    JSON.stringify(payload),
    {
      status,
      headers: {
        "Content-Type":
          "application/json",
      },
    },
  );
}

async function testSelectionAPIClient() {
  const requests = [];

  const fetcher =
    async (url, init = {}) => {
      requests.push({
        url: String(url),
        init,
      });

      return jsonResponse(
        workspaceResponse(
          "select_clip",
          snapshot(
            3,
            [primaryClipId],
            2,
            2,
          ),
        ),
      );
    };

  const client =
    createReviewWorkspaceClient({
      baseUrl:
        "https://example.test/api/v1/",
      fetch: fetcher,
      headers: {
        "X-Review-Test":
          "selection-client",
      },
    });

  const controller =
    new AbortController();

  const response =
    await client.selectClip(
      productionId,
      {
        session_id:
          ` ${sessionId} `,
        clip_id:
          ` ${primaryClipId} `,
        additive: true,
        move_cursor: true,
      },
      {
        signal:
          controller.signal,
      },
    );

  const request = requests[0];
  const body =
    JSON.parse(request.init.body);

  const headers =
    new Headers(
      request.init.headers,
    );

  let invalidClipBlocked = false;

  try {
    await client.selectClip(
      productionId,
      {
        session_id: sessionId,
        clip_id: "   ",
      },
    );
  } catch (error) {
    invalidClipBlocked =
      error instanceof
        ReviewWorkspaceAPIError &&
      error.code ===
        "review_request_validation_failed" &&
      error.status === 422;
  }

  const checks = {
    selection_request_count:
      requests.length === 1,

    selection_method_valid:
      request.init.method === "POST",

    selection_path_valid:
      request.url ===
      `https://example.test/api/v1/productions/${productionId}/review/selection/clip`,

    selection_body_valid:
      body.session_id ===
        sessionId &&
      body.clip_id ===
        primaryClipId &&
      body.additive === true &&
      body.move_cursor === true,

    selection_signal_forwarded:
      request.init.signal ===
        controller.signal,

    selection_headers_valid:
      headers.get("Accept") ===
        "application/json" &&
      headers.get(
        "Content-Type",
      ) === "application/json" &&
      headers.get(
        "X-Review-Test",
      ) === "selection-client",

    selection_response_valid:
      response.success === true &&
      response.operation ===
        "select_clip" &&
      response.snapshot.selection
        .state.active_clip_id ===
        primaryClipId,

    invalid_clip_blocked:
      invalidClipBlocked,

    invalid_request_read_only:
      requests.length === 1,
  };

  return checks;
}

function buildRuntimeClient() {
  const calls = [];

  return {
    calls,

    async openSession(
      currentProductionId,
      request,
      options,
    ) {
      calls.push({
        operation: "open",
        currentProductionId,
        request,
        options,
      });

      return openResponse(
        snapshot(3, [], 1, 1),
      );
    },

    async selectClip(
      currentProductionId,
      request,
      options,
    ) {
      calls.push({
        operation: "select",
        currentProductionId,
        request,
        options,
      });

      const selectedIds =
        request.additive
          ? [
              primaryClipId,
              request.clip_id,
            ].filter(
              (
                clipId,
                index,
                values,
              ) =>
                values.indexOf(
                  clipId,
                ) === index,
            )
          : [request.clip_id];

      return workspaceResponse(
        "select_clip",
        snapshot(
          3,
          selectedIds,
          2,
          2,
        ),
      );
    },
  };
}

async function openRuntime(
  client,
) {
  const runtime =
    createReviewWorkspaceSessionRuntime({
      client,
    });

  await runtime.open(productionId);

  return runtime;
}

async function testSelectionStateRuntime() {
  const client =
    buildRuntimeClient();

  const runtime =
    await openRuntime(client);

  const transitions = [];

  const unsubscribe =
    runtime.subscribe((state) => {
      transitions.push({
        status: state.status,
        pendingOperation:
          state.pendingOperation,
      });

      if (state.snapshot) {
        state.snapshot.metadata
          .listener_mutation = true;
      }
    });

  const before =
    runtime.getState();

  const timelineBefore =
    structuredClone(
      before.snapshot.timeline,
    );

  const historyBefore =
    structuredClone(
      before.snapshot.history,
    );

  const result =
    await runtime.selectClip({
      clip_id: primaryClipId,
      additive: false,
      move_cursor: true,
    });

  const selectionCall =
    client.calls.find(
      (call) =>
        call.operation ===
        "select",
    );

  const selected =
    result.snapshot.selection.state;

  const clonedResult =
    runtime.getState();

  clonedResult.snapshot.selection
    .state.selected_clip_ids.push(
      "external-mutation",
    );

  const isolatedState =
    runtime.getState();

  const checks = {
    selection_transition_valid:
      transitions.some(
        (transition) =>
          transition.status ===
            "selecting" &&
          transition.pendingOperation ===
            "select",
      ) &&
      result.status === "ready" &&
      result.pendingOperation === null,

    selection_request_valid:
      selectionCall
        .currentProductionId ===
        productionId &&
      selectionCall.request
        .session_id === sessionId &&
      selectionCall.request
        .clip_id === primaryClipId &&
      selectionCall.request
        .additive === false &&
      selectionCall.request
        .move_cursor === true,

    selection_snapshot_updated:
      selected.active_clip_id ===
        primaryClipId &&
      selected.selected_clip_ids
        .length === 1 &&
      selected.selected_clip_ids[0] ===
        primaryClipId,

    timeline_revision_unchanged:
      result.snapshot.timeline
        .revision ===
        before.snapshot.timeline
          .revision,

    timeline_payload_unchanged:
      JSON.stringify(
        result.snapshot.timeline,
      ) ===
      JSON.stringify(
        timelineBefore,
      ),

    history_unchanged:
      JSON.stringify(
        result.snapshot.history,
      ) ===
      JSON.stringify(
        historyBefore,
      ),

    no_timeline_command_created:
      result.pendingCommand === null &&
      result.lastCommand === null &&
      result.lastCommandResponse ===
        null,

    state_snapshot_isolated:
      !isolatedState.snapshot
        .selection.state
        .selected_clip_ids.includes(
          "external-mutation",
        ) &&
      isolatedState.snapshot.metadata
        .listener_mutation ===
        undefined,
  };

  unsubscribe();
  runtime.dispose();

  return checks;
}

async function testFailedSelectionIsReadOnly() {
  const client =
    buildRuntimeClient();

  const runtime =
    await openRuntime(client);

  const snapshotBefore =
    runtime.getState().snapshot;

  client.selectClip =
    async () => {
      throw new ReviewWorkspaceAPIError(
        "Clip does not exist.",
        {
          code:
            "review_session_operation_failed",
          status: 409,
          productionId,
          sessionId,
        },
      );
    };

  let failureMapped = false;

  try {
    await runtime.selectClip({
      clip_id:
        "missing-clip",
    });
  } catch {
    const failedState =
      runtime.getState();

    failureMapped =
      failedState.status ===
        "error" &&
      failedState.pendingOperation ===
        null &&
      failedState.error.code ===
        "review_session_operation_failed";
  }

  const snapshotAfter =
    runtime.getState().snapshot;

  const checks = {
    selection_failure_mapped:
      failureMapped,

    selection_failure_read_only:
      JSON.stringify(
        snapshotAfter,
      ) ===
      JSON.stringify(
        snapshotBefore,
      ),
  };

  runtime.dispose();

  return checks;
}

async function testInvalidRevisionIsBlocked() {
  const client =
    buildRuntimeClient();

  const runtime =
    await openRuntime(client);

  const snapshotBefore =
    runtime.getState().snapshot;

  client.selectClip =
    async () =>
      workspaceResponse(
        "select_clip",
        snapshot(
          4,
          [primaryClipId],
          2,
          2,
        ),
      );

  let invalidRevisionBlocked = false;

  try {
    await runtime.selectClip({
      clip_id: primaryClipId,
    });
  } catch (error) {
    invalidRevisionBlocked =
      error instanceof
        ReviewWorkspaceAPIError &&
      error.code ===
        "invalid_response" &&
      error.status === 502;
  }

  const stateAfter =
    runtime.getState();

  const checks = {
    changed_revision_blocked:
      invalidRevisionBlocked,

    changed_revision_read_only:
      JSON.stringify(
        stateAfter.snapshot,
      ) ===
      JSON.stringify(
        snapshotBefore,
      ),
  };

  runtime.dispose();

  return checks;
}

async function testStaleSelectionIgnored() {
  const client =
    buildRuntimeClient();

  const pendingSelections = [];

  client.selectClip =
    (
      currentProductionId,
      request,
      options,
    ) =>
      new Promise((resolve) => {
        pendingSelections.push({
          currentProductionId,
          request,
          options,
          resolve,
        });
      });

  const runtime =
    await openRuntime(client);

  const firstSelection =
    runtime.selectClip({
      clip_id: primaryClipId,
    });

  const secondSelection =
    runtime.selectClip({
      clip_id: secondaryClipId,
    });

  pendingSelections[1].resolve(
    workspaceResponse(
      "select_clip",
      snapshot(
        3,
        [secondaryClipId],
        2,
        2,
      ),
    ),
  );

  await secondSelection;

  pendingSelections[0].resolve(
    workspaceResponse(
      "select_clip",
      snapshot(
        3,
        [primaryClipId],
        2,
        2,
      ),
    ),
  );

  await firstSelection;

  const finalState =
    runtime.getState();

  const checks = {
    stale_selection_ignored:
      finalState.status ===
        "ready" &&
      finalState.snapshot.selection
        .state.active_clip_id ===
        secondaryClipId &&
      finalState.snapshot.selection
        .state.selected_clip_ids[0] ===
        secondaryClipId,
  };

  runtime.dispose();

  return checks;
}

async function main() {
  const checks = {
    ...await testSelectionAPIClient(),
    ...await testSelectionStateRuntime(),
    ...await testFailedSelectionIsReadOnly(),
    ...await testInvalidRevisionIsBlocked(),
    ...await testStaleSelectionIgnored(),
  };

  console.log(
    "=== Frontend Selection API Client & State Runtime ===",
  );

  for (
    const [name, value]
    of Object.entries(checks)
  ) {
    console.log(
      `${name}: ${value}`,
    );

    assert.equal(
      value,
      true,
      `${name} failed`,
    );
  }

  console.log(
    "\nDONE: Frontend Selection API client and state runtime test completed.",
  );
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});