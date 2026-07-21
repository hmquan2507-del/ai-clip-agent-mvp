import type {
  JsonObject,
  ReviewWorkspaceSessionCommandRequest,
} from "./contracts";

export const REVIEW_AI_COMMAND_API_CONTRACT_VERSION =
  "16.6.8" as const;

export type ReviewAICommandOperation =
  "submit_command";

export interface SubmitAICommandRequest
  extends ReviewWorkspaceSessionCommandRequest {
  command_text: string;
  expected_timeline_revision?: number;
  client_request_id?: string;
}

export interface AICommandSubmission {
  contract_version:
    typeof REVIEW_AI_COMMAND_API_CONTRACT_VERSION;
  submission_id: string;
  production_id: string;
  session_id: string;
  command_text: string;
  timeline_revision: number;
  status: "accepted";
  client_request_id: string | null;
  created_at: string;
  metadata: JsonObject;
}

export interface ReviewAICommandSubmissionResponse {
  contract_version:
    typeof REVIEW_AI_COMMAND_API_CONTRACT_VERSION;
  success: true;
  operation: ReviewAICommandOperation;
  production_id: string;
  session_id: string;
  timeline_revision: number;
  submission: AICommandSubmission;
  duplicate: boolean;
  timeline_mutated: false;
}
