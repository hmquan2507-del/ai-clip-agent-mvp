import {
  TIMELINE_UI_INTEGRATION_VERSION,
  type TimelineUiContextMenuState,
  type TimelineUiIntegrationController,
  type TimelineUiIntegrationOptions,
  type TimelineUiIntegrationSnapshot,
  type TimelineUiPointerState,
  type TimelineUiSnapGuide,
  type TimelineUiTool,
  type TimelineUiViewport,
} from "../contracts/professional-timeline-ui-integration-contracts";

function cloneValue<T>(value: T): T {
  return structuredClone(value);
}

function clamp(value: number, minimum: number, maximum: number): number {
  return Math.min(maximum, Math.max(minimum, value));
}

function defaultViewport(
  input: Partial<TimelineUiViewport> = {},
): TimelineUiViewport {
  const zoom = clamp(input.zoom ?? 1, 0.1, 64);
  const pixelsPerFrame = Math.max(
    0.01,
    input.pixelsPerFrame ?? 2 * zoom,
  );

  return {
    zoom,
    scrollFrame: Math.max(0, input.scrollFrame ?? 0),
    widthPx: Math.max(1, input.widthPx ?? 1200),
    pixelsPerFrame,
  };
}

function idlePointer(): TimelineUiPointerState {
  return {
    active: false,
    mode: "none",
    pointerId: null,
    originX: 0,
    currentX: 0,
    originFrame: 0,
    previewFrame: 0,
    clipIds: [],
  };
}

function closedContextMenu(): TimelineUiContextMenuState {
  return {
    open: false,
    x: 0,
    y: 0,
    clipIds: [],
  };
}

export function createTimelineUiIntegrationController(
  options: TimelineUiIntegrationOptions,
): TimelineUiIntegrationController {
  let tool: TimelineUiTool = "select";
  let playheadFrame = Math.max(
    0,
    Math.floor(options.initialPlayheadFrame ?? 0),
  );
  let viewport = defaultViewport(options.initialViewport);
  let pointer = idlePointer();
  let snapGuide: TimelineUiSnapGuide | null = null;
  let contextMenu = closedContextMenu();
  let commandPaletteOpen = false;
  let disposed = false;
  const snapThresholdPx = Math.max(0, options.snapThresholdPx ?? 8);

  const assertActive = (): void => {
    if (disposed) {
      throw new Error("Timeline UI integration controller is disposed.");
    }
  };

  const frameToPixel = (frame: number): number =>
    (frame - viewport.scrollFrame) * viewport.pixelsPerFrame;

  const pixelToFrame = (x: number): number =>
    Math.max(
      0,
      Math.round(
        viewport.scrollFrame + x / viewport.pixelsPerFrame,
      ),
    );

  const getSnapshot = (): TimelineUiIntegrationSnapshot => {
    const commandSnapshot = options.commandRuntime.getSnapshot();
    return {
      version: TIMELINE_UI_INTEGRATION_VERSION,
      document: cloneValue(commandSnapshot.document),
      keyboard: cloneValue(options.keyboardRuntime.getSnapshot()),
      tool,
      playheadFrame,
      viewport: cloneValue(viewport),
      pointer: cloneValue(pointer),
      snapGuide: cloneValue(snapGuide),
      contextMenu: cloneValue(contextMenu),
      commandPaletteOpen,
      canUndo: commandSnapshot.canUndo,
      canRedo: commandSnapshot.canRedo,
      disposed,
    };
  };

  const setTool = (nextTool: TimelineUiTool): void => {
    assertActive();
    tool = nextTool;
    pointer = idlePointer();
    snapGuide = null;
  };

  const setPlayheadFrame = (frame: number): void => {
    assertActive();
    playheadFrame = Math.max(0, Math.floor(frame));
  };

  const setViewport = (
    patch: Partial<TimelineUiViewport>,
  ): void => {
    assertActive();
    viewport = defaultViewport({
      ...viewport,
      ...patch,
      pixelsPerFrame:
        patch.pixelsPerFrame ??
        (patch.zoom !== undefined
          ? 2 * patch.zoom
          : viewport.pixelsPerFrame),
    });
  };

  const selectClip = (
    clipId: string,
    selectionOptions: {
      readonly toggle?: boolean;
      readonly additive?: boolean;
    } = {},
  ): void => {
    assertActive();
    const snapshot = options.commandRuntime.getSnapshot();
    const exists = snapshot.document.clips.some(
      (clip) => clip.id === clipId,
    );
    if (!exists) {
      throw new Error(`Clip not found: ${clipId}`);
    }

    const current = [...snapshot.document.selection];
    let next: string[];

    if (selectionOptions.toggle) {
      next = current.includes(clipId)
        ? current.filter((id) => id !== clipId)
        : [...current, clipId];
    } else if (selectionOptions.additive) {
      next = [...new Set([...current, clipId])];
    } else {
      next = [clipId];
    }

    options.commandRuntime.reset({
      ...snapshot.document,
      version: snapshot.document.version + 1,
      selection: next,
    });
  };

  const marqueeSelect = (
    startFrame: number,
    endFrame: number,
    trackIds?: readonly string[],
  ): void => {
    assertActive();
    const snapshot = options.commandRuntime.getSnapshot();
    const minimum = Math.min(startFrame, endFrame);
    const maximum = Math.max(startFrame, endFrame);
    const trackSet = trackIds ? new Set(trackIds) : null;

    const selected = snapshot.document.clips
      .filter(
        (clip) =>
          (!trackSet || trackSet.has(clip.trackId)) &&
          clip.endFrame >= minimum &&
          clip.startFrame <= maximum,
      )
      .map((clip) => clip.id);

    options.commandRuntime.reset({
      ...snapshot.document,
      version: snapshot.document.version + 1,
      selection: selected,
    });
  };

  const pointerDown = (input: {
    readonly pointerId: number;
    readonly x: number;
    readonly clipIds?: readonly string[];
    readonly mode?: TimelineUiPointerState["mode"];
  }): void => {
    assertActive();
    if (pointer.active) {
      throw new Error("A timeline pointer session is already active.");
    }

    const originFrame = pixelToFrame(input.x);
    pointer = {
      active: true,
      mode:
        input.mode ??
        (tool === "trim"
          ? "trim-end"
          : tool === "hand"
            ? "scrub"
            : "move"),
      pointerId: input.pointerId,
      originX: input.x,
      currentX: input.x,
      originFrame,
      previewFrame: originFrame,
      clipIds: [...(input.clipIds ?? [])],
    };
    snapGuide = null;
  };

  const pointerMove = (input: {
    readonly pointerId: number;
    readonly x: number;
    readonly snapFrames?: readonly number[];
  }): void => {
    assertActive();
    if (!pointer.active || pointer.pointerId !== input.pointerId) {
      return;
    }

    let previewFrame = pixelToFrame(input.x);
    let nextGuide: TimelineUiSnapGuide | null = null;

    for (const frame of input.snapFrames ?? []) {
      const targetX = frameToPixel(frame);
      if (Math.abs(targetX - input.x) <= snapThresholdPx) {
        previewFrame = Math.max(0, Math.floor(frame));
        nextGuide = {
          frame: previewFrame,
          x: targetX,
          label: `Frame ${previewFrame}`,
          visible: true,
        };
        break;
      }
    }

    pointer = {
      ...pointer,
      currentX: input.x,
      previewFrame,
    };
    snapGuide = nextGuide;
  };

  const cancelPointer = (): void => {
    assertActive();
    pointer = idlePointer();
    snapGuide = null;
  };

  const pointerUp = (input: {
    readonly pointerId: number;
    readonly commit?: boolean;
  }): void => {
    assertActive();
    if (!pointer.active || pointer.pointerId !== input.pointerId) {
      return;
    }

    const session = pointer;
    pointer = idlePointer();
    snapGuide = null;

    if (input.commit === false) {
      return;
    }

    const deltaFrames =
      session.previewFrame - session.originFrame;

    if (session.mode === "scrub") {
      playheadFrame = session.previewFrame;
      return;
    }

    if (session.mode === "marquee") {
      marqueeSelect(session.originFrame, session.previewFrame);
      return;
    }

    if (session.clipIds.length === 0 || deltaFrames === 0) {
      return;
    }

    if (session.mode === "move") {
      options.commandRuntime.execute({
        id: `ui-move-${Date.now()}`,
        kind: "move",
        clipIds: session.clipIds,
        deltaFrames,
      });
      return;
    }

    if (
      session.mode === "trim-start" ||
      session.mode === "trim-end"
    ) {
      options.commandRuntime.execute({
        id: `ui-trim-${Date.now()}`,
        kind: "trim",
        clipIds: session.clipIds,
        startDeltaFrames:
          session.mode === "trim-start" ? deltaFrames : 0,
        endDeltaFrames:
          session.mode === "trim-end" ? deltaFrames : 0,
      });
    }
  };

  const splitAtPlayhead = (): void => {
    assertActive();
    options.keyboardRuntime.dispatchCommand(
      "timeline.split",
      { playheadFrame },
    );
  };

  const deleteSelection = (ripple = false): void => {
    assertActive();
    options.keyboardRuntime.dispatchCommand(
      ripple
        ? "timeline.ripple-delete"
        : "timeline.delete",
    );
  };

  const duplicateSelection = (deltaFrames = 1): void => {
    assertActive();
    options.keyboardRuntime.dispatchCommand(
      "timeline.duplicate",
      { command: { deltaFrames } },
    );
  };

  const undo = (): void => {
    assertActive();
    options.keyboardRuntime.dispatchCommand("history.undo");
  };

  const redo = (): void => {
    assertActive();
    options.keyboardRuntime.dispatchCommand("history.redo");
  };

  const openContextMenu = (
    x: number,
    y: number,
    clipIds?: readonly string[],
  ): void => {
    assertActive();
    contextMenu = {
      open: true,
      x,
      y,
      clipIds: [
        ...(clipIds ??
          options.commandRuntime.getSnapshot().document.selection),
      ],
    };
  };

  const closeContextMenu = (): void => {
    assertActive();
    contextMenu = closedContextMenu();
  };

  const openCommandPalette = (): void => {
    assertActive();
    options.keyboardRuntime.dispatchCommand(
      "command-palette.open",
    );
    commandPaletteOpen = true;
  };

  const closeCommandPalette = (): void => {
    assertActive();
    options.keyboardRuntime.closeCommandPalette();
    commandPaletteOpen = false;
  };

  const dispose = (): void => {
    pointer = idlePointer();
    snapGuide = null;
    contextMenu = closedContextMenu();
    commandPaletteOpen = false;
    disposed = true;
  };

  return {
    getSnapshot,
    setTool,
    setPlayheadFrame,
    setViewport,
    frameToPixel,
    pixelToFrame,
    pointerDown,
    pointerMove,
    pointerUp,
    cancelPointer,
    selectClip,
    marqueeSelect,
    splitAtPlayhead,
    deleteSelection,
    duplicateSelection,
    undo,
    redo,
    openContextMenu,
    closeContextMenu,
    openCommandPalette,
    closeCommandPalette,
    dispose,
  };
}
