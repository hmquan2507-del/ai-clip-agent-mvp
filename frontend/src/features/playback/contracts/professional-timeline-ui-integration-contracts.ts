import type {
  TimelineCommandDocument,
  TimelineCommandRuntime,
} from "./professional-timeline-command-contracts";
import type {
  TimelineKeyboardRuntime,
  TimelineKeyboardRuntimeSnapshot,
} from "./professional-timeline-keyboard-contracts";

export const TIMELINE_UI_INTEGRATION_VERSION = "16.9.8" as const;

export type TimelineUiTool =
  | "select"
  | "blade"
  | "hand"
  | "trim"
  | "slip"
  | "slide";

export interface TimelineUiViewport {
  readonly zoom: number;
  readonly scrollFrame: number;
  readonly widthPx: number;
  readonly pixelsPerFrame: number;
}

export interface TimelineUiPointerState {
  readonly active: boolean;
  readonly mode:
    | "none"
    | "marquee"
    | "move"
    | "trim-start"
    | "trim-end"
    | "scrub";
  readonly pointerId: number | null;
  readonly originX: number;
  readonly currentX: number;
  readonly originFrame: number;
  readonly previewFrame: number;
  readonly clipIds: readonly string[];
}

export interface TimelineUiSnapGuide {
  readonly frame: number;
  readonly x: number;
  readonly label: string;
  readonly visible: boolean;
}

export interface TimelineUiContextMenuState {
  readonly open: boolean;
  readonly x: number;
  readonly y: number;
  readonly clipIds: readonly string[];
}

export interface TimelineUiIntegrationSnapshot {
  readonly version: typeof TIMELINE_UI_INTEGRATION_VERSION;
  readonly document: TimelineCommandDocument;
  readonly keyboard: TimelineKeyboardRuntimeSnapshot;
  readonly tool: TimelineUiTool;
  readonly playheadFrame: number;
  readonly viewport: TimelineUiViewport;
  readonly pointer: TimelineUiPointerState;
  readonly snapGuide: TimelineUiSnapGuide | null;
  readonly contextMenu: TimelineUiContextMenuState;
  readonly commandPaletteOpen: boolean;
  readonly canUndo: boolean;
  readonly canRedo: boolean;
  readonly disposed: boolean;
}

export interface TimelineUiIntegrationOptions {
  readonly commandRuntime: TimelineCommandRuntime;
  readonly keyboardRuntime: TimelineKeyboardRuntime;
  readonly initialPlayheadFrame?: number;
  readonly initialViewport?: Partial<TimelineUiViewport>;
  readonly snapThresholdPx?: number;
}

export interface TimelineUiIntegrationController {
  getSnapshot(): TimelineUiIntegrationSnapshot;
  setTool(tool: TimelineUiTool): void;
  setPlayheadFrame(frame: number): void;
  setViewport(viewport: Partial<TimelineUiViewport>): void;
  frameToPixel(frame: number): number;
  pixelToFrame(x: number): number;
  pointerDown(input: {
    readonly pointerId: number;
    readonly x: number;
    readonly clipIds?: readonly string[];
    readonly mode?: TimelineUiPointerState["mode"];
  }): void;
  pointerMove(input: {
    readonly pointerId: number;
    readonly x: number;
    readonly snapFrames?: readonly number[];
  }): void;
  pointerUp(input: {
    readonly pointerId: number;
    readonly commit?: boolean;
  }): void;
  cancelPointer(): void;
  selectClip(
    clipId: string,
    options?: { readonly toggle?: boolean; readonly additive?: boolean },
  ): void;
  marqueeSelect(
    startFrame: number,
    endFrame: number,
    trackIds?: readonly string[],
  ): void;
  splitAtPlayhead(): void;
  deleteSelection(ripple?: boolean): void;
  duplicateSelection(deltaFrames?: number): void;
  undo(): void;
  redo(): void;
  openContextMenu(x: number, y: number, clipIds?: readonly string[]): void;
  closeContextMenu(): void;
  openCommandPalette(): void;
  closeCommandPalette(): void;
  dispose(): void;
}
