import type {
  OpenReviewWorkspaceRequest,
  ReviewRuntimeSessionSnapshot,
  ReviewRuntimeSessionState,
  ReviewWorkspaceAPIErrorCode,
  ReviewWorkspaceCloseResponse,
  ReviewWorkspaceResetResponse,
  ReviewWorkspaceSessionResponse,
  ReviewWorkspaceSnapshotResponse,
} from "../api";

export type ReviewWorkspaceLifecycleStatus =
  | "idle"
  | "opening"
  | "ready"
  | "refreshing"
  | "resetting"
  | "closing"
  | "closed"
  | "error";

export type ReviewWorkspacePendingOperation =
  | "open"
  | "refresh"
  | "reset"
  | "close"
  | null;

export interface ReviewWorkspaceRuntimeError {
  name: string;
  message: string;
  code: ReviewWorkspaceAPIErrorCode | "unknown_error";
  status: number | null;
  technicalMessage: string | null;
  productionId: string | null;
  sessionId: string | null;
}

export interface ReviewWorkspaceRuntimeState {
  status: ReviewWorkspaceLifecycleStatus;
  pendingOperation: ReviewWorkspacePendingOperation;
  productionId: string | null;
  sessionId: string | null;
  session: ReviewRuntimeSessionState | null;
  snapshot: ReviewRuntimeSessionSnapshot | null;
  error: ReviewWorkspaceRuntimeError | null;
  requestRevision: number;
  stateRevision: number;
  updatedAt: string | null;
}

export interface ReviewWorkspaceRuntimeClient {
  openSession(
    productionId: string,
    request?: OpenReviewWorkspaceRequest,
    options?: { signal?: AbortSignal },
  ): Promise<ReviewWorkspaceSessionResponse>;

  getSnapshot(
    productionId: string,
    sessionId?: string | null,
    options?: { signal?: AbortSignal },
  ): Promise<ReviewWorkspaceSnapshotResponse>;

  resetSession(
    productionId: string,
    request: { session_id: string },
    options?: { signal?: AbortSignal },
  ): Promise<ReviewWorkspaceResetResponse>;

  closeSession(
    productionId: string,
    request: { session_id: string },
    options?: { signal?: AbortSignal },
  ): Promise<ReviewWorkspaceCloseResponse>;
}

export interface ReviewWorkspaceRuntimeOpenOptions
  extends OpenReviewWorkspaceRequest {
  signal?: AbortSignal;
}

export interface ReviewWorkspaceRuntimeActionOptions {
  signal?: AbortSignal;
}

export type ReviewWorkspaceRuntimeListener = (
  state: ReviewWorkspaceRuntimeState,
  previousState: ReviewWorkspaceRuntimeState,
) => void;