"use client";

import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";

import type { AiBlock } from "../ai-timeline/types";
import type {
  AiDecisionAction,
  AiDecisionActionAdapter,
  AiDecisionActionIntent,
  AiDecisionActionRecord,
  AiDecisionLifecycleState,
  AiDecisionSelection,
} from "./types";

function nowIso() {
  return new Date().toISOString();
}

function id(prefix: string) {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

function initialState(decision: AiBlock): AiDecisionLifecycleState {
  if (decision.status === "processing") return "processing";
  if (decision.status === "regenerating") return "regenerating";
  if (decision.manual) return "manual";
  if (decision.disabled) return "disabled";
  if (decision.pinned) return "pinned";
  return "applied";
}

function createRecord(decision: AiBlock): AiDecisionActionRecord {
  const state = initialState(decision);
  return {
    decisionId: decision.id,
    state,
    runtimeStatus: "idle",
    pendingAction: null,
    error: null,
    history: [
      {
        id: id("history"),
        action: "generated",
        state,
        createdAt: decision.generatedAt || nowIso(),
        message: "AI decision generated.",
      },
    ],
  };
}

function stateAfterAction(action: AiDecisionAction, previous: AiDecisionLifecycleState): AiDecisionLifecycleState {
  switch (action) {
    case "accept": return "accepted";
    case "reject": return "rejected";
    case "disable": return "disabled";
    case "enable": return "applied";
    case "pin": return "pinned";
    case "unpin": return previous === "pinned" ? "applied" : previous;
    case "convert-to-manual": return "manual";
    case "regenerate": return "regenerating";
    default: return previous;
  }
}

interface AiDecisionActionsContextValue {
  selected: AiDecisionSelection | null;
  selectDecision(decision: AiBlock | null): void;
  getRecord(decision: AiBlock): AiDecisionActionRecord;
  runAction(action: AiDecisionAction, decision?: AiBlock): Promise<void>;
  clearError(decisionId: string): void;
}

const AiDecisionActionsContext = createContext<AiDecisionActionsContextValue | null>(null);

export function AiDecisionActionProvider({
  children,
  adapter,
}: {
  children: ReactNode;
  adapter?: AiDecisionActionAdapter;
}) {
  const [selectedDecision, setSelectedDecision] = useState<AiBlock | null>(null);
  const [records, setRecords] = useState<Record<string, AiDecisionActionRecord>>({});

  const getRecord = useCallback(
    (decision: AiBlock) => records[decision.id] ?? createRecord(decision),
    [records],
  );

  const selectDecision = useCallback((decision: AiBlock | null) => {
    setSelectedDecision(decision);
    if (!decision) return;
    setRecords((current) => current[decision.id] ? current : { ...current, [decision.id]: createRecord(decision) });
  }, []);

  const runAction = useCallback(async (action: AiDecisionAction, explicitDecision?: AiBlock) => {
    const decision = explicitDecision ?? selectedDecision;
    if (!decision) return;

    const request: AiDecisionActionIntent = { action, decision, clientRequestId: id("decision-action") };
    const previous = records[decision.id] ?? createRecord(decision);
    const optimisticState = stateAfterAction(action, previous.state);

    setRecords((current) => ({
      ...current,
      [decision.id]: {
        ...(current[decision.id] ?? previous),
        state: optimisticState,
        runtimeStatus: adapter ? "pending" : "pending-runtime",
        pendingAction: adapter ? action : null,
        error: null,
        history: [
          ...(current[decision.id]?.history ?? previous.history),
          {
            id: id("history"),
            action,
            state: optimisticState,
            createdAt: nowIso(),
            message: adapter ? "Action submitted to runtime." : "UI action recorded; backend runtime is not connected.",
          },
        ],
      },
    }));

    if (!adapter) return;

    try {
      const result = await adapter(request);
      setRecords((current) => ({
        ...current,
        [decision.id]: {
          ...(current[decision.id] ?? previous),
          state: result.status === "pending-runtime" ? optimisticState : stateAfterAction(action, previous.state),
          runtimeStatus: result.status,
          pendingAction: null,
          error: null,
        },
      }));
    } catch (error) {
      const message = error instanceof Error ? error.message : "AI decision action failed.";
      setRecords((current) => ({
        ...current,
        [decision.id]: {
          ...(current[decision.id] ?? previous),
          state: "error",
          runtimeStatus: "error",
          pendingAction: null,
          error: message,
          history: [
            ...(current[decision.id]?.history ?? previous.history),
            { id: id("history"), action, state: "error", createdAt: nowIso(), message },
          ],
        },
      }));
    }
  }, [adapter, records, selectedDecision]);

  const clearError = useCallback((decisionId: string) => {
    setRecords((current) => current[decisionId] ? {
      ...current,
      [decisionId]: { ...current[decisionId], error: null, runtimeStatus: "idle" },
    } : current);
  }, []);

  const selected = useMemo<AiDecisionSelection | null>(() => {
    if (!selectedDecision) return null;
    return { decision: selectedDecision, record: records[selectedDecision.id] ?? createRecord(selectedDecision) };
  }, [records, selectedDecision]);

  const value = useMemo(() => ({ selected, selectDecision, getRecord, runAction, clearError }), [selected, selectDecision, getRecord, runAction, clearError]);

  return <AiDecisionActionsContext.Provider value={value}>{children}</AiDecisionActionsContext.Provider>;
}

export function useAiDecisionActions() {
  const value = useContext(AiDecisionActionsContext);
  if (!value) throw new Error("useAiDecisionActions must be used inside AiDecisionActionProvider.");
  return value;
}
