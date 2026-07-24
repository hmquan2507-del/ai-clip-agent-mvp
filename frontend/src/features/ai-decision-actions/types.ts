import type { AiBlock } from "../ai-timeline/types";

export type AiDecisionLifecycleState =
  | "draft"
  | "applied"
  | "accepted"
  | "rejected"
  | "disabled"
  | "pinned"
  | "manual"
  | "regenerating"
  | "processing"
  | "stale"
  | "error";

export type AiDecisionAction =
  | "accept"
  | "reject"
  | "disable"
  | "enable"
  | "pin"
  | "unpin"
  | "duplicate"
  | "convert-to-manual"
  | "regenerate"
  | "explain"
  | "compare";

export type AiDecisionActionRuntimeStatus = "idle" | "pending" | "pending-runtime" | "success" | "error";

export interface AiDecisionActionIntent {
  action: AiDecisionAction;
  decision: AiBlock;
  clientRequestId: string;
}

export interface AiDecisionActionResult {
  status: "success" | "pending-runtime";
  message?: string;
}

export type AiDecisionActionAdapter = (
  intent: AiDecisionActionIntent,
) => Promise<AiDecisionActionResult> | AiDecisionActionResult;

export interface AiDecisionHistoryEntry {
  id: string;
  action: AiDecisionAction | "generated";
  state: AiDecisionLifecycleState;
  createdAt: string;
  message?: string;
}

export interface AiDecisionActionRecord {
  decisionId: string;
  state: AiDecisionLifecycleState;
  runtimeStatus: AiDecisionActionRuntimeStatus;
  pendingAction: AiDecisionAction | null;
  error: string | null;
  history: AiDecisionHistoryEntry[];
}

export interface AiDecisionSelection {
  decision: AiBlock;
  record: AiDecisionActionRecord;
}
