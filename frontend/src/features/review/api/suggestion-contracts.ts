import type {
  JsonObject,
  ReviewRuntimeSessionSnapshot,
  ReviewWorkspaceSessionCommandRequest,
} from "./contracts";

export const REVIEW_AI_SUGGESTION_API_CONTRACT_VERSION =
  "16.6.4" as const;

export const AI_SUGGESTION_CONTRACT_VERSION =
  "16.6.1" as const;

export type ReviewAISuggestionOperation =
  | "get_suggestions"
  | "select_suggestion"
  | "apply_suggestion"
  | "dismiss_suggestion"
  | "regenerate_suggestions";

export type AISuggestionKind =
  | "hook"
  | "pacing"
  | "broll"
  | "subtitle"
  | "music"
  | "sound_effect"
  | "transition"
  | "generic";

export type AISuggestionStatus =
  | "proposed"
  | "applied"
  | "dismissed"
  | "stale";

export type AISuggestionTargetType =
  | "timeline"
  | "track"
  | "clip"
  | "range";

export interface AISuggestionTarget {
  production_id: string;
  target_type: AISuggestionTargetType;
  track_id: string | null;
  clip_id: string | null;
  start_time: number | null;
  end_time: number | null;
  metadata: JsonObject;
}

export interface AISuggestionCommandProposal {
  operation: string;
  arguments: JsonObject;
  metadata: JsonObject;
}

export interface AISuggestion {
  contract_version:
    typeof AI_SUGGESTION_CONTRACT_VERSION;
  suggestion_id: string;
  production_id: string;
  kind: AISuggestionKind;
  status: AISuggestionStatus;
  title: string;
  description: string;
  timeline_revision: number;
  target: AISuggestionTarget;
  command: AISuggestionCommandProposal | null;
  score: number | null;
  actionable: boolean;
  stale: boolean;
  created_at: string;
  metadata: JsonObject;
}

export interface AISuggestionReadModel {
  contract_version:
    typeof AI_SUGGESTION_CONTRACT_VERSION;
  production_id: string;
  timeline_revision: number;
  suggestions: AISuggestion[];
  selected_suggestion_id: string | null;
  count: number;
  actionable_count: number;
  stale_count: number;
  generated_at: string;
  metadata: JsonObject;
}

export interface AISuggestionLifecycleSnapshot {
  contract_version:
    typeof AI_SUGGESTION_CONTRACT_VERSION;
  production_id: string;
  lifecycle_revision: number;
  timeline_revision: number;
  read_model: AISuggestionReadModel;
  created_at: string;
  metadata: JsonObject;
}

export interface ReviewAISuggestionRequest
  extends ReviewWorkspaceSessionCommandRequest {
  expected_lifecycle_revision?: number;
}

export interface SelectAISuggestionRequest
  extends ReviewAISuggestionRequest {
  suggestion_id?: string | null;
}

export interface ApplyAISuggestionRequest
  extends ReviewAISuggestionRequest {
  suggestion_id: string;
  expected_timeline_revision?: number;
}

export interface DismissAISuggestionRequest
  extends ReviewAISuggestionRequest {
  suggestion_id: string;
}

export type RegenerateAISuggestionsRequest =
  ReviewAISuggestionRequest;

export interface ReviewAISuggestionResponse {
  contract_version:
    typeof REVIEW_AI_SUGGESTION_API_CONTRACT_VERSION;
  success: true;
  operation: ReviewAISuggestionOperation;
  production_id: string;
  session_id: string;
  timeline_revision: number;
  lifecycle_revision: number;
  workspace_snapshot: ReviewRuntimeSessionSnapshot;
  suggestion_snapshot: AISuggestionLifecycleSnapshot;
  timeline_command_result: JsonObject | null;
  metadata: JsonObject;
}
