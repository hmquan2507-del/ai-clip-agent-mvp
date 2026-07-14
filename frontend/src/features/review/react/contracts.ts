import type { ReactNode } from "react";

import type {
  ReviewWorkspaceClientConfig,
  ReviewRuntimeSessionSnapshot,
  ReviewRuntimeSessionState,
} from "../api";

import type {
  ReviewWorkspaceRuntimeActionOptions,
  ReviewWorkspaceRuntimeOpenOptions,
  ReviewWorkspaceRuntimeState,
} from "../state/contracts";

import type {
  ReviewWorkspaceSessionRuntime,
} from "../state/runtime";

export interface ReviewWorkspaceActions {
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
  status: ReviewWorkspaceRuntimeState["status"];
  pendingOperation:
    ReviewWorkspaceRuntimeState["pendingOperation"];
  idle: boolean;
  loading: boolean;
  ready: boolean;
  refreshing: boolean;
  resetting: boolean;
  closing: boolean;
  closed: boolean;
  failed: boolean;
  error: ReviewWorkspaceRuntimeState["error"];
}

export interface ReviewWorkspaceSessionView {
  productionId: string | null;
  sessionId: string | null;
  session: ReviewRuntimeSessionState | null;
}

export interface ReviewWorkspaceSnapshotView {
  snapshot: ReviewRuntimeSessionSnapshot | null;
  available: boolean;
}