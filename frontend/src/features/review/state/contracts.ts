import type {
  ClearTimelineClipboardHistoryRequest,
  ClearTimelineClipboardRequest,
  CloseTimelineGapRequest,
  CopyTimelineClipsRequest,
  CutTimelineClipsRequest,
  DeleteTimelineClipRequest,
  DeleteTimelineClipsRequest,
  DuplicateTimelineClipRequest,
  DuplicateTimelineClipsRequest,
  MoveTimelineClipRequest,
  MoveTimelineClipsRequest,
  OpenReviewWorkspaceRequest,
  PasteTimelineClipsRequest,
  RedoTimelineCommandRequest,
  RestoreTimelineClipboardHistoryRequest,
  ReviewClipboardCommandResponse,
  ReviewClipboardOperation,
  AISuggestionLifecycleSnapshot,
  ReviewAICommandSubmissionResponse,
  ApplyAISuggestionRequest,
  DismissAISuggestionRequest,
  RegenerateAISuggestionsRequest,
  ReviewAISuggestionOperation,
  ReviewAISuggestionResponse,
  ReviewRuntimeSessionSnapshot,
  ReviewRuntimeSessionState,
  ReviewTimelineCommandOperation,
  ReviewTimelineCommandResponse,
  ReviewWorkspaceAPIErrorCode,
  ReviewWorkspaceCloseResponse,
  ReviewWorkspaceResetResponse,
  ReviewWorkspaceSessionResponse,
  ReviewWorkspaceSnapshotResponse,
  SelectAISuggestionRequest,
  SelectTimelineClipRequest,
  SubmitAICommandRequest,
  SplitTimelineClipRequest,
  TrimTimelineClipEndRequest,
  TrimTimelineClipStartRequest,
  UndoTimelineCommandRequest,
} from "../api";

export type ReviewWorkspaceLifecycleStatus =
  | "idle"
  | "opening"
  | "ready"
  | "refreshing"
  | "resetting"
  | "selecting"
  | "executing"
  | "suggesting"
  | "submitting_command"
  | "closing"
  | "closed"
  | "error";

export type ReviewWorkspacePendingOperation =
  | "open"
  | "refresh"
  | "reset"
  | "select"
  | "timeline_command"
  | "clipboard_command"
  | "ai_suggestion"
  | "ai_command_submission"
  | "close"
  | null;

export interface ReviewWorkspaceRuntimeError {
  name: string;
  message: string;

  code:
    | ReviewWorkspaceAPIErrorCode
    | "unknown_error";

  status: number | null;
  technicalMessage: string | null;
  productionId: string | null;
  sessionId: string | null;

  isRevisionConflict: boolean;
  expectedRevision: number | null;
  currentRevision: number | null;
}

export interface ReviewWorkspaceRuntimeState {
  status: ReviewWorkspaceLifecycleStatus;

  pendingOperation:
    ReviewWorkspacePendingOperation;

  pendingCommand:
    ReviewTimelineCommandOperation | null;

  lastCommand:
    ReviewTimelineCommandOperation | null;

  lastCommandResponse:
    ReviewTimelineCommandResponse | null;

  pendingClipboardOperation:
    ReviewClipboardOperation | null;

  lastClipboardOperation:
    ReviewClipboardOperation | null;

  lastClipboardResponse:
    ReviewClipboardCommandResponse | null;

  pendingSuggestionOperation:
    ReviewAISuggestionOperation | null;

  lastSuggestionOperation:
    ReviewAISuggestionOperation | null;

  lastSuggestionResponse:
    ReviewAISuggestionResponse | null;

  suggestionSnapshot:
    AISuggestionLifecycleSnapshot | null;

  aiCommandSubmissionPending: boolean;
  lastAICommandSubmission:
    ReviewAICommandSubmissionResponse | null;

  productionId: string | null;
  sessionId: string | null;

  session:
    ReviewRuntimeSessionState | null;

  snapshot:
    ReviewRuntimeSessionSnapshot | null;

  error:
    ReviewWorkspaceRuntimeError | null;

  requestRevision: number;
  stateRevision: number;
  updatedAt: string | null;
}

export interface ReviewWorkspaceRuntimeClient {
  openSession(
    productionId: string,
    request?: OpenReviewWorkspaceRequest,
    options?: {
      signal?: AbortSignal;
    },
  ): Promise<ReviewWorkspaceSessionResponse>;

  getSnapshot(
    productionId: string,
    sessionId?: string | null,
    options?: {
      signal?: AbortSignal;
    },
  ): Promise<ReviewWorkspaceSnapshotResponse>;

  resetSession(
    productionId: string,
    request: {
      session_id: string;
    },
    options?: {
      signal?: AbortSignal;
    },
  ): Promise<ReviewWorkspaceResetResponse>;

  closeSession(
    productionId: string,
    request: {
      session_id: string;
    },
    options?: {
      signal?: AbortSignal;
    },
  ): Promise<ReviewWorkspaceCloseResponse>;

  selectClip(
    productionId: string,
    request: SelectTimelineClipRequest,
    options?: {
      signal?: AbortSignal;
    },
  ): Promise<ReviewWorkspaceSnapshotResponse>;

  moveClip(
    productionId: string,
    request: MoveTimelineClipRequest,
    options?: {
      signal?: AbortSignal;
    },
  ): Promise<ReviewTimelineCommandResponse>;

  moveClips(
    productionId: string,
    request: MoveTimelineClipsRequest,
    options?: { signal?: AbortSignal },
  ): Promise<ReviewTimelineCommandResponse>;

  trimClipStart(
    productionId: string,
    request: TrimTimelineClipStartRequest,
    options?: {
      signal?: AbortSignal;
    },
  ): Promise<ReviewTimelineCommandResponse>;

  trimClipEnd(
    productionId: string,
    request: TrimTimelineClipEndRequest,
    options?: {
      signal?: AbortSignal;
    },
  ): Promise<ReviewTimelineCommandResponse>;

  splitClip(
    productionId: string,
    request: SplitTimelineClipRequest,
    options?: {
      signal?: AbortSignal;
    },
  ): Promise<ReviewTimelineCommandResponse>;

  duplicateClip(
    productionId: string,
    request: DuplicateTimelineClipRequest,
    options?: {
      signal?: AbortSignal;
    },
  ): Promise<ReviewTimelineCommandResponse>;

  duplicateClips(
    productionId: string,
    request: DuplicateTimelineClipsRequest,
    options?: { signal?: AbortSignal },
  ): Promise<ReviewTimelineCommandResponse>;

  deleteClip(
    productionId: string,
    request: DeleteTimelineClipRequest,
    options?: {
      signal?: AbortSignal;
    },
  ): Promise<ReviewTimelineCommandResponse>;

  deleteClips(
    productionId: string,
    request: DeleteTimelineClipsRequest,
    options?: { signal?: AbortSignal },
  ): Promise<ReviewTimelineCommandResponse>;

  closeGap(
    productionId: string,
    request: CloseTimelineGapRequest,
    options?: {
      signal?: AbortSignal;
    },
  ): Promise<ReviewTimelineCommandResponse>;

  undoTimeline(
    productionId: string,
    request: UndoTimelineCommandRequest,
    options?: {
      signal?: AbortSignal;
    },
  ): Promise<ReviewTimelineCommandResponse>;

  redoTimeline(
    productionId: string,
    request: RedoTimelineCommandRequest,
    options?: {
      signal?: AbortSignal;
    },
  ): Promise<ReviewTimelineCommandResponse>;

  copyTimelineClips(
    productionId: string,
    request: CopyTimelineClipsRequest,
    options?: { signal?: AbortSignal },
  ): Promise<ReviewClipboardCommandResponse>;

  cutTimelineClips(
    productionId: string,
    request: CutTimelineClipsRequest,
    options?: { signal?: AbortSignal },
  ): Promise<ReviewClipboardCommandResponse>;

  pasteTimelineClips(
    productionId: string,
    request: PasteTimelineClipsRequest,
    options?: { signal?: AbortSignal },
  ): Promise<ReviewClipboardCommandResponse>;

  restoreTimelineClipboardHistory(
    productionId: string,
    request: RestoreTimelineClipboardHistoryRequest,
    options?: { signal?: AbortSignal },
  ): Promise<ReviewClipboardCommandResponse>;

  clearTimelineClipboard(
    productionId: string,
    request: ClearTimelineClipboardRequest,
    options?: { signal?: AbortSignal },
  ): Promise<ReviewClipboardCommandResponse>;

  clearTimelineClipboardHistory(
    productionId: string,
    request: ClearTimelineClipboardHistoryRequest,
    options?: { signal?: AbortSignal },
  ): Promise<ReviewClipboardCommandResponse>;

  getAISuggestions(
    productionId: string,
    sessionId: string,
    options?: { signal?: AbortSignal },
  ): Promise<ReviewAISuggestionResponse>;

  selectAISuggestion(
    productionId: string,
    request: SelectAISuggestionRequest,
    options?: { signal?: AbortSignal },
  ): Promise<ReviewAISuggestionResponse>;

  applyAISuggestion(
    productionId: string,
    request: ApplyAISuggestionRequest,
    options?: { signal?: AbortSignal },
  ): Promise<ReviewAISuggestionResponse>;

  dismissAISuggestion(
    productionId: string,
    request: DismissAISuggestionRequest,
    options?: { signal?: AbortSignal },
  ): Promise<ReviewAISuggestionResponse>;

  regenerateAISuggestions(
    productionId: string,
    request: RegenerateAISuggestionsRequest,
    options?: { signal?: AbortSignal },
  ): Promise<ReviewAISuggestionResponse>;

  submitAICommand(
    productionId: string,
    request: SubmitAICommandRequest,
    options?: { signal?: AbortSignal },
  ): Promise<ReviewAICommandSubmissionResponse>;
}

export interface ReviewWorkspaceRuntimeOpenOptions
  extends OpenReviewWorkspaceRequest {
  signal?: AbortSignal;
}

export interface ReviewWorkspaceRuntimeActionOptions {
  signal?: AbortSignal;
}

export type SelectTimelineClipInput = Omit<
  SelectTimelineClipRequest,
  "session_id"
>;

export type MoveTimelineClipInput = Omit<
  MoveTimelineClipRequest,
  "session_id" | "expected_revision"
>;

export type MoveTimelineClipsInput = Omit<
  MoveTimelineClipsRequest,
  "session_id" | "expected_revision"
>;

export type DuplicateTimelineClipsInput = Omit<
  DuplicateTimelineClipsRequest,
  "session_id" | "expected_revision"
>;

export type DeleteTimelineClipsInput = Omit<
  DeleteTimelineClipsRequest,
  "session_id" | "expected_revision"
>;

export type TrimTimelineClipStartInput = Omit<
  TrimTimelineClipStartRequest,
  "session_id" | "expected_revision"
>;

export type TrimTimelineClipEndInput = Omit<
  TrimTimelineClipEndRequest,
  "session_id" | "expected_revision"
>;

export type SplitTimelineClipInput = Omit<
  SplitTimelineClipRequest,
  "session_id" | "expected_revision"
>;

export type DuplicateTimelineClipInput = Omit<
  DuplicateTimelineClipRequest,
  "session_id" | "expected_revision"
>;

export type DeleteTimelineClipInput = Omit<
  DeleteTimelineClipRequest,
  "session_id" | "expected_revision"
>;

export type CloseTimelineGapInput = Omit<
  CloseTimelineGapRequest,
  "session_id" | "expected_revision"
>;

export type CopyTimelineClipsInput = Omit<
  CopyTimelineClipsRequest,
  "session_id" | "expected_revision"
>;

export type CutTimelineClipsInput = Omit<
  CutTimelineClipsRequest,
  "session_id" | "expected_revision"
>;

export type PasteTimelineClipsInput = Omit<
  PasteTimelineClipsRequest,
  "session_id" | "expected_revision"
>;

export type RestoreTimelineClipboardHistoryInput = Omit<
  RestoreTimelineClipboardHistoryRequest,
  "session_id" | "expected_revision"
>;

export interface SelectAISuggestionInput {
  suggestion_id: string | null;
}

export interface ApplyAISuggestionInput {
  suggestion_id: string;
}

export interface DismissAISuggestionInput {
  suggestion_id: string;
}

export type SubmitAICommandInput = Omit<
  SubmitAICommandRequest,
  "session_id" | "expected_timeline_revision"
>;

export type ReviewWorkspaceRuntimeListener = (
  state: ReviewWorkspaceRuntimeState,
  previousState: ReviewWorkspaceRuntimeState,
) => void;
