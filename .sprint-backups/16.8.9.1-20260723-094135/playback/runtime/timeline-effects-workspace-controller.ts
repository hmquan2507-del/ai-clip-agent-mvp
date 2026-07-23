import {
  TIMELINE_EFFECTS_WORKSPACE_CONTRACT_VERSION,
  type TimelineEffectsAddEffectInput,
  type TimelineEffectsAddKeyframeInput,
  type TimelineEffectsWorkspaceDependencies,
  type TimelineEffectsWorkspaceListener,
  type TimelineEffectsWorkspaceState,
} from "../contracts/timeline-effects-workspace-contracts";
import type {
  TimelineEffectDefinition,
  TimelineEffectsAnimationFrame,
  TimelineHistoryJsonValue,
  TimelineKeyframe,
  TimelineTransitionDefinition,
} from "../contracts";
import { TimelineEffectsAnimationRuntime } from "./timeline-effects-animation-runtime";
import { TimelineEffectsHistoryBridge } from "./timeline-effects-history-bridge";

export interface TimelineEffectsWorkspaceControllerOptions {
  readonly idFactory?: () => string;
  readonly now?: () => number;
}

const defaultIdFactory = () => `effects-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;

export class TimelineEffectsWorkspaceController {
  private readonly listeners = new Set<TimelineEffectsWorkspaceListener>();
  private readonly disposers: Array<() => void> = [];
  private readonly idFactory: () => string;
  private version = 0;
  private status: TimelineEffectsWorkspaceState["status"] = "detached";
  private selectedClipIds: readonly string[] = Object.freeze([]);
  private currentTimeSeconds = 0;
  private frame: TimelineEffectsAnimationFrame | null = null;
  private lastError: string | null = null;
  private dependencies: TimelineEffectsWorkspaceDependencies = {};

  constructor(
    readonly runtime: TimelineEffectsAnimationRuntime,
    private readonly history?: TimelineEffectsHistoryBridge<TimelineHistoryJsonValue>,
    options: TimelineEffectsWorkspaceControllerOptions = {},
  ) {
    this.idFactory = options.idFactory ?? defaultIdFactory;
  }

  attach(dependencies: TimelineEffectsWorkspaceDependencies): void {
    this.detach();
    this.dependencies = dependencies;
    this.status = "idle";
    if (dependencies.selection) {
      this.selectedClipIds = Object.freeze([...dependencies.selection.getSelectedClipIds()]);
      this.disposers.push(dependencies.selection.subscribe((clipIds) => {
        this.selectedClipIds = Object.freeze([...clipIds]);
        void this.refreshPreview();
      }));
    }
    if (dependencies.playhead) {
      this.currentTimeSeconds = dependencies.playhead.getCurrentTimeSeconds();
      this.disposers.push(dependencies.playhead.subscribe((timeSeconds) => {
        this.currentTimeSeconds = Math.max(0, timeSeconds);
        void this.refreshPreview();
      }));
    }
    void this.refreshPreview();
  }

  detach(): void {
    while (this.disposers.length) this.disposers.pop()?.();
    this.dependencies = {};
    this.status = "detached";
    this.frame = null;
    this.emit();
  }

  dispose(): void {
    this.detach();
    this.status = "disposed";
    this.listeners.clear();
  }

  subscribe(listener: TimelineEffectsWorkspaceListener): () => void {
    this.listeners.add(listener);
    listener(this.getState());
    return () => this.listeners.delete(listener);
  }

  getState(): TimelineEffectsWorkspaceState {
    const activeClipId = this.selectedClipIds[0] ?? null;
    return Object.freeze({
      contractVersion: TIMELINE_EFFECTS_WORKSPACE_CONTRACT_VERSION,
      version: this.version,
      status: this.status,
      attached: this.status !== "detached" && this.status !== "disposed",
      busy: this.status === "applying",
      selectedClipIds: this.selectedClipIds,
      activeClipId,
      currentTimeSeconds: this.currentTimeSeconds,
      frame: this.frame,
      keyframes: activeClipId ? this.runtime.animation.getKeyframes(activeClipId) : Object.freeze([]),
      effects: activeClipId ? this.runtime.effects.getEffects(activeClipId) : Object.freeze([]),
      transitions: activeClipId ? this.runtime.transitions.getTransitions().filter((item) => item.fromClipId === activeClipId || item.toClipId === activeClipId) : Object.freeze([]),
      presets: this.runtime.presets.getPresets(),
      lastError: this.lastError,
    });
  }

  setSelection(clipIds: readonly string[]): void {
    this.selectedClipIds = Object.freeze([...clipIds]);
    void this.refreshPreview();
  }

  setCurrentTime(timeSeconds: number): void {
    this.currentTimeSeconds = Math.max(0, timeSeconds);
    void this.refreshPreview();
  }

  async addKeyframe(input: TimelineEffectsAddKeyframeInput): Promise<TimelineKeyframe> {
    const clipId = this.requireActiveClip();
    const keyframe: TimelineKeyframe = Object.freeze({
      keyframeId: this.idFactory(),
      clipId,
      property: input.property,
      timeSeconds: input.timeSeconds ?? this.currentTimeSeconds,
      value: input.value,
      interpolation: input.interpolation ?? "ease-in-out",
    });
    await this.mutate(`Add ${input.property} keyframe`, "effects:keyframe", [{ path: `clips.${clipId}.keyframes.${keyframe.keyframeId}`, before: null, after: keyframe as unknown as TimelineHistoryJsonValue }], () => this.runtime.addKeyframe(keyframe));
    return keyframe;
  }

  async removeKeyframe(keyframeId: string): Promise<boolean> {
    const existing = this.runtime.animation.getKeyframes().find((item) => item.keyframeId === keyframeId);
    if (!existing) return false;
    await this.mutate("Remove keyframe", "effects:keyframe", [{ path: `clips.${existing.clipId}.keyframes.${keyframeId}`, before: existing as unknown as TimelineHistoryJsonValue, after: null }], () => this.runtime.removeKeyframe(keyframeId));
    return true;
  }

  async addEffect(input: TimelineEffectsAddEffectInput): Promise<TimelineEffectDefinition> {
    const clipId = this.requireActiveClip();
    const effect: TimelineEffectDefinition = Object.freeze({
      effectId: this.idFactory(), clipId, kind: input.kind, label: input.label, enabled: true,
      order: this.runtime.effects.getEffects(clipId).length,
      parameters: Object.freeze({ ...(input.parameters ?? {}) }),
    });
    await this.mutate(`Add ${effect.label}`, "effects:stack", [{ path: `clips.${clipId}.effects.${effect.effectId}`, before: null, after: effect as unknown as TimelineHistoryJsonValue }], () => this.runtime.addEffect(effect));
    return effect;
  }

  async updateEffectParameters(effectId: string, parameters: Readonly<Record<string, TimelineHistoryJsonValue>>): Promise<void> {
    const before = this.runtime.effects.getEffects().find((item) => item.effectId === effectId);
    if (!before) throw new Error(`Unknown effect: ${effectId}`);
    await this.mutate(`Update ${before.label}`, `effects:${effectId}`, [{ path: `clips.${before.clipId}.effects.${effectId}.parameters`, before: before.parameters, after: Object.freeze({ ...before.parameters, ...parameters }) }], () => this.runtime.updateEffectParameters(effectId, parameters));
  }

  async toggleEffect(effectId: string, enabled: boolean): Promise<void> {
    const before = this.runtime.effects.getEffects().find((item) => item.effectId === effectId);
    if (!before) throw new Error(`Unknown effect: ${effectId}`);
    await this.mutate(`${enabled ? "Enable" : "Disable"} ${before.label}`, `effects:${effectId}`, [{ path: `clips.${before.clipId}.effects.${effectId}.enabled`, before: before.enabled, after: enabled }], () => this.runtime.setEffectEnabled(effectId, enabled));
  }

  async removeEffect(effectId: string): Promise<boolean> {
    const before = this.runtime.effects.getEffects().find((item) => item.effectId === effectId);
    if (!before) return false;
    await this.mutate(`Remove ${before.label}`, "effects:stack", [{ path: `clips.${before.clipId}.effects.${effectId}`, before: before as unknown as TimelineHistoryJsonValue, after: null }], () => this.runtime.removeEffect(effectId));
    return true;
  }

  async applyPreset(presetId: string): Promise<readonly TimelineKeyframe[]> {
    const clipId = this.requireActiveClip();
    let created: readonly TimelineKeyframe[] = [];
    await this.mutate(`Apply motion preset ${presetId}`, "effects:preset", [{ path: `clips.${clipId}.presets`, before: null, after: presetId }], () => { created = this.runtime.applyPreset(presetId, clipId, this.currentTimeSeconds, this.idFactory); });
    return created;
  }

  async addTransition(transition: Omit<TimelineTransitionDefinition, "transitionId">): Promise<TimelineTransitionDefinition> {
    const created = Object.freeze({ ...transition, transitionId: this.idFactory() });
    await this.mutate(`Add ${created.kind} transition`, "effects:transition", [{ path: `transitions.${created.transitionId}`, before: null, after: created as unknown as TimelineHistoryJsonValue }], () => this.runtime.addTransition(created));
    return created;
  }

  async refreshPreview(): Promise<void> {
    const clipId = this.selectedClipIds[0] ?? null;
    try {
      if (!clipId) {
        this.frame = null;
        await this.dependencies.preview?.clear();
      } else {
        this.frame = this.runtime.evaluateFrame(clipId, this.currentTimeSeconds);
        await this.dependencies.preview?.applyFrame(this.frame);
      }
      this.lastError = null;
      if (this.status !== "detached" && this.status !== "disposed") this.status = "idle";
    } catch (error) {
      this.status = "error";
      this.lastError = error instanceof Error ? error.message : String(error);
    }
    this.emit();
  }

  private requireActiveClip(): string {
    const clipId = this.selectedClipIds[0];
    if (!clipId) throw new Error("Select a timeline clip before editing effects or animation.");
    return clipId;
  }

  private async mutate(label: string, mergeKey: string, changes: readonly { path: string; before: TimelineHistoryJsonValue; after: TimelineHistoryJsonValue }[], operation: () => void | Promise<void>): Promise<void> {
    this.status = "applying";
    this.emit();
    try {
      if (this.history) {
        await this.history.execute({ commandId: this.idFactory(), label, mergeKey, changes: changes.map((change) => ({ ...change, kind: "replace" as const })), execute: operation });
      } else await operation();
      this.lastError = null;
      this.status = "idle";
      await this.refreshPreview();
    } catch (error) {
      this.status = "error";
      this.lastError = error instanceof Error ? error.message : String(error);
      this.emit();
      throw error;
    }
  }

  private emit(): void {
    this.version += 1;
    const state = this.getState();
    this.listeners.forEach((listener) => listener(state));
  }
}
