"use client";

import type React from "react";
import { useEffect, useState } from "react";
import type { TimelineAnimatableProperty, TimelineEffectKind } from "../contracts/timeline-effects-animation-contracts";
import type { TimelineEffectsWorkspaceState } from "../contracts/timeline-effects-workspace-contracts";
import { TimelineEffectsWorkspaceController } from "../runtime/timeline-effects-workspace-controller";

export interface TimelineEffectsWorkspaceUiProps {
  readonly controller: TimelineEffectsWorkspaceController;
  readonly className?: string;
}

function useEffectsWorkspace(controller: TimelineEffectsWorkspaceController): TimelineEffectsWorkspaceState {
  const [state, setState] = useState(() => controller.getState());
  useEffect(() => controller.subscribe(setState), [controller]);
  return state;
}

const properties: readonly TimelineAnimatableProperty[] = ["position-x", "position-y", "scale-x", "scale-y", "rotation", "opacity", "volume", "blur", "brightness", "contrast", "saturation"];
const effectKinds: readonly TimelineEffectKind[] = ["transform", "opacity", "blur", "brightness", "contrast", "saturation", "color-adjustment", "audio-gain"];

export function TimelineEffectsInspector({ controller, className = "" }: TimelineEffectsWorkspaceUiProps) {
  const state = useEffectsWorkspace(controller);
  const [property, setProperty] = useState<TimelineAnimatableProperty>("opacity");
  const [value, setValue] = useState("1");
  const [effectKind, setEffectKind] = useState<TimelineEffectKind>("blur");
  if (!state.activeClipId) return <aside className={`timeline-effects-inspector p-4 text-sm opacity-70 ${className}`} aria-label="Effects and animation inspector">Select a clip to edit effects and animation.</aside>;
  return (
    <aside className={`timeline-effects-inspector flex h-full w-80 flex-col overflow-auto border-l ${className}`} aria-label="Effects and animation inspector">
      <header className="border-b p-3"><h2 className="font-semibold">Effects & Animation</h2><p className="text-xs opacity-60">Clip: {state.activeClipId}</p></header>
      <section className="space-y-3 border-b p-3" aria-labelledby="animation-heading">
        <h3 id="animation-heading" className="font-medium">Animation</h3>
        <div className="grid grid-cols-2 gap-2"><select aria-label="Animated property" value={property} onChange={(event: React.ChangeEvent<HTMLSelectElement>) => setProperty(event.target.value as TimelineAnimatableProperty)} className="rounded border px-2 py-1">{properties.map((item) => <option key={item} value={item}>{item}</option>)}</select><input aria-label="Keyframe value" type="number" step="0.01" value={value} onChange={(event: React.ChangeEvent<HTMLInputElement>) => setValue(event.target.value)} className="rounded border px-2 py-1" /></div>
        <button type="button" disabled={state.busy || !Number.isFinite(Number(value))} onClick={() => void controller.addKeyframe({ property, value: Number(value) })} className="rounded border px-3 py-1">Add keyframe at {state.currentTimeSeconds.toFixed(2)}s</button>
        <div role="list" className="space-y-1">{state.keyframes.map((item) => <div role="listitem" key={item.keyframeId} className="flex items-center justify-between rounded border p-2 text-xs"><span>{item.property}: {item.value} @ {item.timeSeconds.toFixed(2)}s</span><button type="button" aria-label={`Delete ${item.property} keyframe`} onClick={() => void controller.removeKeyframe(item.keyframeId)}>×</button></div>)}</div>
      </section>
      <section className="space-y-3 border-b p-3" aria-labelledby="presets-heading"><h3 id="presets-heading" className="font-medium">Motion presets</h3><div className="grid grid-cols-2 gap-2">{state.presets.map((preset) => <button type="button" disabled={state.busy} key={preset.presetId} onClick={() => void controller.applyPreset(preset.presetId)} className="rounded border px-2 py-1 text-sm">{preset.label}</button>)}</div></section>
      <section className="space-y-3 p-3" aria-labelledby="effects-heading"><h3 id="effects-heading" className="font-medium">Effect stack</h3><div className="flex gap-2"><select aria-label="Effect kind" value={effectKind} onChange={(event: React.ChangeEvent<HTMLSelectElement>) => setEffectKind(event.target.value as TimelineEffectKind)} className="min-w-0 flex-1 rounded border px-2 py-1">{effectKinds.map((item) => <option key={item} value={item}>{item}</option>)}</select><button type="button" disabled={state.busy} onClick={() => void controller.addEffect({ kind: effectKind, label: effectKind.replaceAll("-", " ") })} className="rounded border px-2 py-1">Add</button></div><div role="list" className="space-y-2">{state.effects.map((effect) => <div role="listitem" key={effect.effectId} className="rounded border p-2"><div className="flex items-center justify-between"><label className="flex items-center gap-2"><input type="checkbox" checked={effect.enabled} onChange={(event: React.ChangeEvent<HTMLInputElement>) => void controller.toggleEffect(effect.effectId, event.target.checked)} />{effect.label}</label><button type="button" aria-label={`Remove ${effect.label}`} onClick={() => void controller.removeEffect(effect.effectId)}>×</button></div></div>)}</div></section>
      {state.lastError ? <div role="alert" className="m-3 rounded border p-2 text-sm">{state.lastError}</div> : null}
    </aside>
  );
}

export function TimelineEffectsWorkspaceStatusBar({ controller, className = "" }: TimelineEffectsWorkspaceUiProps) {
  const state = useEffectsWorkspace(controller);
  return <div className={`timeline-effects-status flex items-center gap-3 text-xs ${className}`} role="status" aria-live="polite"><span>{state.busy ? "Applying…" : "Effects ready"}</span><span>{state.keyframes.length} keyframes</span><span>{state.effects.length} effects</span><span>{state.transitions.length} transitions</span></div>;
}
