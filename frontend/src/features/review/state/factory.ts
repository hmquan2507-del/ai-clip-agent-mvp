import {
  createReviewWorkspaceClient,
  type ReviewWorkspaceClientConfig,
} from "../api";

import type {
  ReviewWorkspaceRuntimeClient,
} from "./contracts";

import {
  ReviewWorkspaceSessionRuntime,
} from "./runtime";

export interface ReviewWorkspaceSessionRuntimeConfig {
  client?: ReviewWorkspaceRuntimeClient;
  api?: ReviewWorkspaceClientConfig;
}

export function createReviewWorkspaceSessionRuntime(
  config:
    ReviewWorkspaceSessionRuntimeConfig = {},
): ReviewWorkspaceSessionRuntime {
  const client =
    config.client ??
    createReviewWorkspaceClient(config.api);

  return new ReviewWorkspaceSessionRuntime(
    client,
  );
}