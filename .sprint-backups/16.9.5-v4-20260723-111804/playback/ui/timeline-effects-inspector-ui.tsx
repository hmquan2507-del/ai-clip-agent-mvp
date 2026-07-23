"use client";

import type React from "react";
import { useEffect, useMemo, useState } from "react";
import type { TimelineAnimatableProperty, TimelineInterpolation, TimelineTransitionKind } from "../contracts";
import { TimelineEffectsInspectorController, TimelineEffectsWorkspaceController } from "../runtime";

export interface TimelineEffectsAnimationInspectorProps {
  readonly controller: TimelineEffectsWorkspaceController;
  readonly inspector?: TimelineEffectsInspectorController;
  readonly neighboringClipIds?: readonly string[];
  readonly className?: string;
}

function useWorkspace(controller: TimelineEffectsWorkspaceController) {
  const [state, setState] = useState(() => controller.getState());
  useEffect(() => controller.subscribe(setState), [controller]);
  return state;
}

function Section({ title, children, defaultOpen = true }: { readonly title: string; readonly children: React.ReactNode; readonly defaultOpen?: boolean }) {
  return <details open={defaultOpen} className="border-b"><summary className="cursor-pointer select-none px-3 py-2 text-sm font-semibold">{title}</summary><div className="space-y-3 px-3 pb-3">{children}</div></details>;
}

export function TimelineEffectsAnimationInspector({ controller, inspector: suppliedInspector, neighboringClipIds = [], className = "" }: TimelineEffectsAnimationInspectorProps) {
  const state = useWorkspace(controller);
  const inspector = useMemo(() => suppliedInspector ?? new TimelineEffectsInspectorController(), [suppliedInspector]);
  const descriptors = inspector.getPropertyDescriptors();
  const [selectedProperty, setSelectedProperty] = useState<TimelineAnimatableProperty>(inspector.getSelectedProperty());
  const descriptor = descriptors.find((item) => item.property === selectedProperty) ?? descriptors[0];
  const frameValue = state.frame?.properties[selectedProperty];
  const [value, setValue] = useState<number>(typeof frameValue === "number" ? frameValue : descriptor.defaultValue);
  const [interpolation, setInterpolation] = useState<TimelineInterpolation>(inspector.getInterpolation());
  const [search, setSearch] = useState("");
  const [transitionKind, setTransitionKind] = useState<TimelineTransitionKind>("cross-dissolve");
  const [transitionDuration, setTransitionDuration] = useState(0.35);
  const [targetClipId, setTargetClipId] = useState(neighboringClipIds[0] ?? "");

  useEffect(() => {
    const next = state.frame?.properties[selectedProperty];
    if (typeof next === "number") setValue(next);
  }, [state.frame, selectedProperty]);

  inspector.setSearchQuery(search);
  const effects = inspector.getEffectCatalog();
  const transitions = inspector.getTransitionCatalog();
  const activeKeyframes = state.keyframes.filter((item) => item.property === selectedProperty);

  if (!state.activeClipId) return <aside className={`flex h-full w-80 items-center justify-center border-l p-6 text-center text-sm opacity-70 ${className}`} aria-label="Effects and animation inspector">Select a clip to open the Effects & Animation inspector.</aside>;

  return <aside className={`flex h-full w-80 flex-col overflow-hidden border-l bg-background ${className}`} aria-label="Effects and animation inspector">
    <header className="border-b p-3"><div className="flex items-center justify-between"><div><h2 className="font-semibold">Effects & Animation</h2><p className="max-w-52 truncate text-xs opacity-60">{state.activeClipId}</p></div><span className="rounded border px-2 py-1 text-[10px]">{state.busy ? "Applying…" : "Ready"}</span></div></header>
    <div className="flex-1 overflow-y-auto">
      <Section title="Transform & keyframes">
        <label className="block text-xs font-medium">Property<select className="mt-1 w-full rounded border px-2 py-1.5" value={selectedProperty} onChange={(event) => { const property = event.target.value as TimelineAnimatableProperty; inspector.setSelectedProperty(property); setSelectedProperty(property); const nextDescriptor = descriptors.find((item) => item.property === property); setValue(state.frame?.properties[property] ?? nextDescriptor?.defaultValue ?? 0); }}>{descriptors.map((item) => <option key={item.property} value={item.property}>{item.label}</option>)}</select></label>
        <div className="grid grid-cols-[1fr_76px] gap-2"><input aria-label={`${descriptor.label} slider`} type="range" min={descriptor.min} max={descriptor.max} step={descriptor.step} value={value} onChange={(event) => setValue(Number(event.target.value))}/><div className="flex items-center rounded border"><input aria-label={`${descriptor.label} value`} className="min-w-0 flex-1 bg-transparent px-2 py-1 text-right text-sm" type="number" min={descriptor.min} max={descriptor.max} step={descriptor.step} value={value} onChange={(event) => setValue(inspector.clamp(selectedProperty, Number(event.target.value)))}/><span className="pr-1 text-[10px] opacity-60">{descriptor.unit}</span></div></div>
        <label className="block text-xs font-medium">Interpolation<select className="mt-1 w-full rounded border px-2 py-1.5" value={interpolation} onChange={(event) => { const next = event.target.value as TimelineInterpolation; inspector.setInterpolation(next); setInterpolation(next); }}><option value="hold">Hold</option><option value="linear">Linear</option><option value="ease-in">Ease in</option><option value="ease-out">Ease out</option><option value="ease-in-out">Ease in/out</option></select></label>
        <button className="w-full rounded border px-3 py-2 text-sm font-medium" type="button" disabled={state.busy} onClick={() => void controller.addKeyframe({ property: selectedProperty, value, interpolation })}>◆ Add keyframe at {state.currentTimeSeconds.toFixed(2)}s</button>
        <div className="space-y-1" role="list" aria-label={`${descriptor.label} keyframes`}>{activeKeyframes.map((keyframe) => <button type="button" key={keyframe.keyframeId} className="flex w-full items-center justify-between rounded border px-2 py-1.5 text-xs" onClick={() => controller.setCurrentTime(keyframe.timeSeconds)}><span>{keyframe.timeSeconds.toFixed(2)}s · {keyframe.value}</span><span role="button" tabIndex={0} aria-label={`Delete keyframe at ${keyframe.timeSeconds.toFixed(2)} seconds`} onClick={(event) => { event.stopPropagation(); void controller.removeKeyframe(keyframe.keyframeId); }}>×</span></button>)}</div>
      </Section>

      <Section title="Motion presets"><div className="grid grid-cols-2 gap-2">{state.presets.map((preset) => <button type="button" disabled={state.busy} key={preset.presetId} onClick={() => void controller.applyPreset(preset.presetId)} className="rounded border p-2 text-left"><strong className="block text-xs">{preset.label}</strong><span className="text-[10px] opacity-60">{preset.durationSeconds.toFixed(2)}s · {preset.keyframes.length} keys</span></button>)}</div></Section>

      <Section title="Effect browser"><input type="search" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search effects…" className="w-full rounded border px-2 py-1.5 text-sm"/><div className="space-y-2">{effects.map((effect) => <div key={effect.kind} className="rounded border p-2"><div className="flex items-start justify-between gap-2"><div><strong className="block text-xs">{effect.label}</strong><p className="text-[10px] opacity-60">{effect.description}</p></div><button type="button" className="rounded border px-2 py-1 text-xs" disabled={state.busy} onClick={() => void controller.addEffect({ kind: effect.kind, label: effect.label, parameters: effect.defaultParameters })}>Add</button></div></div>)}</div></Section>

      <Section title={`Effect stack (${state.effects.length})`}>{state.effects.length === 0 ? <p className="text-xs opacity-60">No effects on this clip.</p> : <div className="space-y-2">{state.effects.map((effect) => <div key={effect.effectId} className="rounded border p-2"><div className="flex items-center justify-between"><label className="flex items-center gap-2 text-xs font-medium"><input type="checkbox" checked={effect.enabled} onChange={(event) => void controller.toggleEffect(effect.effectId, event.target.checked)}/>{effect.label}</label><button aria-label={`Remove ${effect.label}`} type="button" onClick={() => void controller.removeEffect(effect.effectId)}>×</button></div>{Object.entries(effect.parameters).map(([name, parameter]) => typeof parameter === "number" ? <label key={name} className="mt-2 grid grid-cols-[1fr_72px] items-center gap-2 text-[10px]"><span>{name}</span><input className="rounded border px-1 py-0.5 text-right" type="number" step="0.01" value={parameter} onChange={(event) => void controller.updateEffectParameters(effect.effectId, { [name]: Number(event.target.value) })}/></label> : null)}</div>)}</div>}</Section>

      <Section title="Transitions" defaultOpen={false}><label className="block text-xs">To clip<select className="mt-1 w-full rounded border px-2 py-1.5" value={targetClipId} onChange={(event) => setTargetClipId(event.target.value)}><option value="">Select adjacent clip</option>{neighboringClipIds.filter((id) => id !== state.activeClipId).map((id) => <option key={id} value={id}>{id}</option>)}</select></label><label className="block text-xs">Transition<select className="mt-1 w-full rounded border px-2 py-1.5" value={transitionKind} onChange={(event) => { const kind = event.target.value as TimelineTransitionKind; setTransitionKind(kind); const item = transitions.find((candidate) => candidate.kind === kind); if (item) setTransitionDuration(item.defaultDurationSeconds); }}>{transitions.map((item) => <option key={item.kind} value={item.kind}>{item.label}</option>)}</select></label><label className="block text-xs">Duration<input className="mt-1 w-full rounded border px-2 py-1.5" type="number" min="0.05" max="5" step="0.05" value={transitionDuration} onChange={(event) => setTransitionDuration(Math.max(0.05, Number(event.target.value)))}/></label><button type="button" className="w-full rounded border px-3 py-2 text-sm" disabled={!targetClipId || state.busy} onClick={() => void controller.addTransition({ kind: transitionKind, fromClipId: state.activeClipId!, toClipId: targetClipId, startSeconds: state.currentTimeSeconds, durationSeconds: transitionDuration, enabled: true, parameters: {} })}>Add transition</button></Section>
    </div>
    <footer className="border-t px-3 py-2 text-[10px] opacity-70" role="status" aria-live="polite">{state.keyframes.length} keyframes · {state.effects.length} effects · {state.transitions.length} transitions</footer>
    {state.lastError ? <div role="alert" className="border-t p-2 text-xs">{state.lastError}</div> : null}
  </aside>;
}
