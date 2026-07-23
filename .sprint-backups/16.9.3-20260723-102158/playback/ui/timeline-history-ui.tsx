"use client";

import type React from "react";
import { useEffect, useMemo, useRef, useState } from "react";
import type { TimelineHistoryCheckpoint, TimelineHistoryEntry, TimelineHistoryJsonValue } from "../contracts/timeline-history-contracts";
import type { TimelineHistoryUiState } from "../contracts/timeline-history-ui-contracts";
import { TimelineHistoryUiController } from "../runtime/timeline-history-ui-controller";

const shortcut = (redo = false) => `${typeof navigator !== "undefined" && /Mac|iPhone|iPad/.test(navigator.platform) ? "⌘" : "Ctrl"}${redo ? " + Shift" : ""} + Z`;

export interface TimelineHistoryUiProps<TState = TimelineHistoryJsonValue> {
  readonly controller: TimelineHistoryUiController<TState>;
  readonly className?: string;
}

function useHistoryUi<TState>(controller: TimelineHistoryUiController<TState>): TimelineHistoryUiState<TState> {
  const [state, setState] = useState(() => controller.getState());
  useEffect(() => controller.subscribe(setState), [controller]);
  return state;
}

export function TimelineHistoryToolbar<TState = TimelineHistoryJsonValue>({ controller, className = "" }: TimelineHistoryUiProps<TState>) {
  const state = useHistoryUi(controller);
  return (
    <div className={`timeline-history-toolbar flex items-center gap-1 ${className}`} role="toolbar" aria-label="Timeline history controls">
      <button type="button" aria-label={state.undoLabel ? `Undo ${state.undoLabel}` : "Undo"} title={`${state.undoLabel ? `Undo ${state.undoLabel}` : "Undo"} (${shortcut()})`} disabled={!state.canUndo || state.busy} onClick={() => void controller.undo()} className="rounded px-2 py-1 disabled:opacity-40">↶ <span className="sr-only sm:not-sr-only">Undo</span></button>
      <button type="button" aria-label={state.redoLabel ? `Redo ${state.redoLabel}` : "Redo"} title={`${state.redoLabel ? `Redo ${state.redoLabel}` : "Redo"} (${shortcut(true)})`} disabled={!state.canRedo || state.busy} onClick={() => void controller.redo()} className="rounded px-2 py-1 disabled:opacity-40">↷ <span className="sr-only sm:not-sr-only">Redo</span></button>
      <button type="button" aria-expanded={state.panelMode === "history"} onClick={() => controller.togglePanel("history")} className="rounded px-2 py-1">● History</button>
      <button type="button" aria-expanded={state.panelMode === "checkpoints"} onClick={() => controller.togglePanel("checkpoints")} className="rounded px-2 py-1">⏺ Checkpoint</button>
      {state.busy ? <span role="status" aria-live="polite" className="text-xs">Working…</span> : null}
    </div>
  );
}

function HistoryEntryRow<TState>({ entry, current, selected, onSelect }: { entry: TimelineHistoryEntry<TState>; current: boolean; selected: boolean; onSelect: () => void }) {
  return <button type="button" data-entry-id={entry.entryId} aria-current={current ? "step" : undefined} onClick={onSelect} className={`w-full rounded px-3 py-2 text-left ${current ? "font-semibold ring-1" : ""} ${selected ? "bg-black/10" : ""}`}><span aria-hidden="true">{current ? "●" : "○"}</span> {entry.label}</button>;
}

export function TimelineHistoryPanel<TState = TimelineHistoryJsonValue>({ controller, className = "" }: TimelineHistoryUiProps<TState>) {
  const state = useHistoryUi(controller);
  const currentRef = useRef<HTMLDivElement | null>(null);
  useEffect(() => { currentRef.current?.querySelector<HTMLElement>("[aria-current='step']")?.scrollIntoView({ block: "nearest" }); }, [state.currentEntryId]);
  if (state.panelMode === "closed") return null;
  return (
    <aside className={`timeline-history-panel flex h-full min-h-0 w-80 flex-col border-l ${className}`} aria-label="Timeline history panel">
      <header className="flex items-center justify-between border-b p-3"><h2 className="font-semibold">{state.panelMode === "history" ? "History" : "Checkpoints"}</h2><button type="button" aria-label="Close history panel" onClick={() => controller.closePanel()}>×</button></header>
      {state.panelMode === "history" ? <div ref={currentRef} role="list" className="min-h-0 flex-1 space-y-1 overflow-auto p-2">{state.entries.length ? state.entries.map((entry) => <div role="listitem" key={entry.entryId}><HistoryEntryRow entry={entry} current={entry.entryId === state.currentEntryId} selected={entry.entryId === state.selectedEntryId} onSelect={() => void controller.selectEntry(entry)} /></div>) : <p className="p-3 text-sm opacity-60">No editing operations yet.</p>}</div> : <TimelineCheckpointList controller={controller} />}
      <footer className="border-t p-3 text-xs" aria-label="History status">{state.integration.history.past.length} operations · Undo: {state.canUndo ? "Yes" : "No"} · Redo: {state.canRedo ? "Yes" : "No"} · Checkpoints: {state.checkpoints.length}</footer>
    </aside>
  );
}

function TimelineCheckpointList<TState>({ controller }: { controller: TimelineHistoryUiController<TState> }) {
  const state = useHistoryUi(controller);
  const [label, setLabel] = useState("");
  return <div className="min-h-0 flex-1 overflow-auto p-3"><form className="mb-3 flex gap-2" onSubmit={(event: React.FormEvent<HTMLFormElement>) => { event.preventDefault(); void controller.createCheckpoint(label).then(() => setLabel("")); }}><input aria-label="Checkpoint name" value={label} onChange={(event: React.ChangeEvent<HTMLInputElement>) => setLabel(event.target.value)} placeholder="Checkpoint name" className="min-w-0 flex-1 rounded border px-2 py-1" /><button type="submit" disabled={!label.trim() || state.busy} className="rounded border px-2 py-1">Create</button></form><div role="list" className="space-y-2">{state.checkpoints.map((checkpoint: TimelineHistoryCheckpoint<TState>) => <div role="listitem" key={checkpoint.checkpointId} className={`rounded border p-2 ${checkpoint.checkpointId === state.selectedCheckpointId ? "ring-1" : ""}`}><div className="font-medium">{checkpoint.label}</div><div className="mt-2 flex gap-2"><button type="button" disabled={state.busy} onClick={() => void controller.restoreCheckpoint(checkpoint)} className="rounded border px-2 py-1 text-xs">Restore</button><button type="button" disabled={state.busy || checkpoint.protected} onClick={() => void controller.deleteCheckpoint(checkpoint)} className="rounded border px-2 py-1 text-xs">Delete</button></div></div>)}</div></div>;
}

export function TimelineHistoryToast<TState = TimelineHistoryJsonValue>({ controller, className = "" }: TimelineHistoryUiProps<TState>) {
  const state = useHistoryUi(controller);
  useEffect(() => { if (!state.toast) return; const timer = window.setTimeout(() => controller.dismissToast(), 2600); return () => window.clearTimeout(timer); }, [controller, state.toast]);
  if (!state.toast) return null;
  return <div className={`timeline-history-toast fixed bottom-4 right-4 rounded border bg-white p-3 shadow-lg ${className}`} role={state.toast.kind === "error" ? "alert" : "status"} aria-live="polite"><strong>{state.toast.title}</strong><p className="text-sm">{state.toast.description}</p><button type="button" aria-label="Dismiss notification" onClick={() => controller.dismissToast()} className="absolute right-1 top-1">×</button></div>;
}

export function TimelineHistoryContextMenu<TState = TimelineHistoryJsonValue>({ controller, className = "" }: TimelineHistoryUiProps<TState>) {
  const state = useHistoryUi(controller);
  const items = useMemo(() => [{ label: "Undo", disabled: !state.canUndo, action: () => controller.undo() }, { label: "Redo", disabled: !state.canRedo, action: () => controller.redo() }, { label: "History", disabled: false, action: () => controller.togglePanel("history") }, { label: "Checkpoints", disabled: false, action: () => controller.togglePanel("checkpoints") }], [controller, state.canRedo, state.canUndo]);
  return <div role="menu" aria-label="Timeline history menu" className={`min-w-40 rounded border bg-white p-1 shadow ${className}`}>{items.map((item) => <button type="button" role="menuitem" key={item.label} disabled={item.disabled || state.busy} onClick={() => void item.action()} className="block w-full rounded px-2 py-1 text-left disabled:opacity-40">{item.label}</button>)}</div>;
}

export function TimelineHistoryUi<TState = TimelineHistoryJsonValue>({ controller, className = "" }: TimelineHistoryUiProps<TState>) {
  return <div className={className}><TimelineHistoryToolbar controller={controller} /><TimelineHistoryPanel controller={controller} /><TimelineHistoryToast controller={controller} /></div>;
}
