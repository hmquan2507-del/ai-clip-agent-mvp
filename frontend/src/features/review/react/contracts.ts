import type {
  ReactNode,
} from "react";

import type {
  AISuggestion,
  AISuggestionLifecycleSnapshot,
  ReviewWorkspaceClientConfig,
  ReviewRuntimeSessionSnapshot,
  ReviewRuntimeSessionState,
} from "../api";

import type {
  ApplyAISuggestionInput,
  CloseTimelineGapInput,
  CopyTimelineClipsInput,
  CutTimelineClipsInput,
  DeleteTimelineClipInput,
  DeleteTimelineClipsInput,
  DismissAISuggestionInput,
  DuplicateTimelineClipInput,
  DuplicateTimelineClipsInput,
  MoveTimelineClipInput,
  MoveTimelineClipsInput,
  PasteTimelineClipsInput,
  ReviewWorkspaceRuntimeActionOptions,
  ReviewWorkspaceRuntimeOpenOptions,
  ReviewWorkspaceRuntimeState,
  RestoreTimelineClipboardHistoryInput,
  SelectAISuggestionInput,
  SubmitAICommandInput,
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

  moveClips(
    input: MoveTimelineClipsInput,
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

  duplicateClips(
    input: DuplicateTimelineClipsInput,
    options?: ReviewWorkspaceRuntimeActionOptions,
  ): Promise<ReviewWorkspaceRuntimeState>;

  deleteClip(
    input: DeleteTimelineClipInput,
    options?: ReviewWorkspaceRuntimeActionOptions,
  ): Promise<ReviewWorkspaceRuntimeState>;

  deleteClips(
    input: DeleteTimelineClipsInput,
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

export interface ReviewTimelineClipboardActions {
  copyTimelineClips(
    input: CopyTimelineClipsInput,
    options?: ReviewWorkspaceRuntimeActionOptions,
  ): Promise<ReviewWorkspaceRuntimeState>;

  cutTimelineClips(
    input: CutTimelineClipsInput,
    options?: ReviewWorkspaceRuntimeActionOptions,
  ): Promise<ReviewWorkspaceRuntimeState>;

  pasteTimelineClips(
    input: PasteTimelineClipsInput,
    options?: ReviewWorkspaceRuntimeActionOptions,
  ): Promise<ReviewWorkspaceRuntimeState>;

  restoreTimelineClipboardHistory(
    input: RestoreTimelineClipboardHistoryInput,
    options?: ReviewWorkspaceRuntimeActionOptions,
  ): Promise<ReviewWorkspaceRuntimeState>;

  clearTimelineClipboard(
    options?: ReviewWorkspaceRuntimeActionOptions,
  ): Promise<ReviewWorkspaceRuntimeState>;

  clearTimelineClipboardHistory(
    options?: ReviewWorkspaceRuntimeActionOptions,
  ): Promise<ReviewWorkspaceRuntimeState>;
}

export interface ReviewAISuggestionActions {
  refreshAISuggestions(
    options?: ReviewWorkspaceRuntimeActionOptions,
  ): Promise<ReviewWorkspaceRuntimeState>;

  selectAISuggestion(
    input: SelectAISuggestionInput,
    options?: ReviewWorkspaceRuntimeActionOptions,
  ): Promise<ReviewWorkspaceRuntimeState>;

  applyAISuggestion(
    input: ApplyAISuggestionInput,
    options?: ReviewWorkspaceRuntimeActionOptions,
  ): Promise<ReviewWorkspaceRuntimeState>;

  dismissAISuggestion(
    input: DismissAISuggestionInput,
    options?: ReviewWorkspaceRuntimeActionOptions,
  ): Promise<ReviewWorkspaceRuntimeState>;

  regenerateAISuggestions(
    options?: ReviewWorkspaceRuntimeActionOptions,
  ): Promise<ReviewWorkspaceRuntimeState>;
}

export interface ReviewAICommandActions {
  submitAICommand(
    input: SubmitAICommandInput,
    options?: ReviewWorkspaceRuntimeActionOptions,
  ): Promise<ReviewWorkspaceRuntimeState>;
}

export interface ReviewWorkspaceActions
  extends
    ReviewTimelineSelectionActions,
    ReviewTimelineCommandActions,
    ReviewTimelineClipboardActions,
    ReviewAISuggestionActions,
    ReviewAICommandActions {
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
  autoLoadSuggestions?: boolean;

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

  pendingClipboardOperation:
    ReviewWorkspaceRuntimeState[
      "pendingClipboardOperation"
    ];

  pendingSuggestionOperation:
    ReviewWorkspaceRuntimeState[
      "pendingSuggestionOperation"
    ];

  aiCommandSubmissionPending: boolean;

  idle: boolean;
  loading: boolean;
  ready: boolean;
  refreshing: boolean;
  resetting: boolean;
  selecting: boolean;
  executing: boolean;
  executingClipboard: boolean;
  suggesting: boolean;
  submittingCommand: boolean;
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

export interface ReviewAISuggestionView {
  snapshot: AISuggestionLifecycleSnapshot | null;
  suggestions: AISuggestion[];
  selectedSuggestion: AISuggestion | null;
  available: boolean;
  pending: boolean;
  operation:
    ReviewWorkspaceRuntimeState[
      "pendingSuggestionOperation"
    ];
  lifecycleRevision: number | null;
  timelineRevision: number | null;
}
