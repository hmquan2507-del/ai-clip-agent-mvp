import type {
  ReactNode,
} from "react";

import type {
  ReviewWorkspaceClientConfig,
  ReviewRuntimeSessionSnapshot,
  ReviewRuntimeSessionState,
} from "../api";

import type {
  CloseTimelineGapInput,
  DeleteTimelineClipInput,
  DuplicateTimelineClipInput,
  MoveTimelineClipInput,
  ReviewWorkspaceRuntimeActionOptions,
  ReviewWorkspaceRuntimeOpenOptions,
  ReviewWorkspaceRuntimeState,
  SelectTimelineClipInput,
  SplitTimelineClipInput,
  TrimTimelineClipEndInput,
  TrimTimelineClipStartInput,
} from "../state/contracts";

import type {
  ReviewWorkspaceSessionRuntime,
} from "../state/runtime";

export interface ReviewTimelineSelectionActions {
  selectClip(
    input: SelectTimelineClipInput,
    options?: ReviewWorkspaceRuntimeActionOptions,
  ): Promise<ReviewWorkspaceRuntimeState>;
}

export interface ReviewTimelineCommandActions {
  moveClip(
    input: MoveTimelineClipInput,
    options?: ReviewWorkspaceRuntimeActionOptions,
  ): Promise<ReviewWorkspaceRuntimeState>;

  trimClipStart(
    input: TrimTimelineClipStartInput,
    options?: ReviewWorkspaceRuntimeActionOptions,
  ): Promise<ReviewWorkspaceRuntimeState>;

  trimClipEnd(
    input: TrimTimelineClipEndInput,
    options?: ReviewWorkspaceRuntimeActionOptions,
  ): Promise<ReviewWorkspaceRuntimeState>;

  splitClip(
    input: SplitTimelineClipInput,
    options?: ReviewWorkspaceRuntimeActionOptions,
  ): Promise<ReviewWorkspaceRuntimeState>;

  duplicateClip(
    input: DuplicateTimelineClipInput,
    options?: ReviewWorkspaceRuntimeActionOptions,
  ): Promise<ReviewWorkspaceRuntimeState>;

  deleteClip(
    input: DeleteTimelineClipInput,
    options?: ReviewWorkspaceRuntimeActionOptions,
  ): Promise<ReviewWorkspaceRuntimeState>;

  closeGap(
    input: CloseTimelineGapInput,
    options?: ReviewWorkspaceRuntimeActionOptions,
  ): Promise<ReviewWorkspaceRuntimeState>;

  undoTimeline(
    options?: ReviewWorkspaceRuntimeActionOptions,
  ): Promise<ReviewWorkspaceRuntimeState>;

  redoTimeline(
    options?: ReviewWorkspaceRuntimeActionOptions,
  ): Promise<ReviewWorkspaceRuntimeState>;
}

export interface ReviewWorkspaceActions
  extends
    ReviewTimelineSelectionActions,
    ReviewTimelineCommandActions {
  open(
    options?: ReviewWorkspaceRuntimeOpenOptions,
  ): Promise<ReviewWorkspaceRuntimeState>;

  refresh(
    options?: ReviewWorkspaceRuntimeActionOptions,
  ): Promise<ReviewWorkspaceRuntimeState>;

  reset(
    options?: ReviewWorkspaceRuntimeActionOptions,
  ): Promise<ReviewWorkspaceRuntimeState>;

  close(
    options?: ReviewWorkspaceRuntimeActionOptions,
  ): Promise<ReviewWorkspaceRuntimeState>;

  clear(): ReviewWorkspaceRuntimeState;
}

export interface ReviewWorkspaceContextValue {
  productionId: string;
  runtime: ReviewWorkspaceSessionRuntime;
  state: ReviewWorkspaceRuntimeState;
  actions: ReviewWorkspaceActions;
}

export interface ReviewWorkspaceProviderProps {
  productionId: string;
  children: ReactNode;
  runtime?: ReviewWorkspaceSessionRuntime;
  api?: ReviewWorkspaceClientConfig;
  autoOpen?: boolean;

  openOptions?: Omit<
    ReviewWorkspaceRuntimeOpenOptions,
    "signal"
  >;

  onError?: (error: unknown) => void;
}

export interface ReviewWorkspaceStatusView {
  status:
    ReviewWorkspaceRuntimeState["status"];

  pendingOperation:
    ReviewWorkspaceRuntimeState[
      "pendingOperation"
    ];

  pendingCommand:
    ReviewWorkspaceRuntimeState[
      "pendingCommand"
    ];

  idle: boolean;
  loading: boolean;
  ready: boolean;
  refreshing: boolean;
  resetting: boolean;
  selecting: boolean;
  executing: boolean;
  closing: boolean;
  closed: boolean;
  failed: boolean;

  error:
    ReviewWorkspaceRuntimeState["error"];
}

export interface ReviewWorkspaceSessionView {
  productionId: string | null;
  sessionId: string | null;

  session:
    ReviewRuntimeSessionState | null;
}

export interface ReviewWorkspaceSnapshotView {
  snapshot:
    ReviewRuntimeSessionSnapshot | null;

  available: boolean;
}