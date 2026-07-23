import type { TimelineEffectDefinition } from "../contracts/timeline-effects-animation-contracts";
import type { TimelineHistoryJsonValue } from "../contracts/timeline-history-contracts";

export class TimelineEffectStackRuntime {
  private readonly effects = new Map<string, TimelineEffectDefinition>();

  addEffect(effect: TimelineEffectDefinition): TimelineEffectDefinition {
    if (this.effects.has(effect.effectId)) throw new Error(`Effect already exists: ${effect.effectId}`);
    return this.upsertEffect(effect);
  }

  upsertEffect(effect: TimelineEffectDefinition): TimelineEffectDefinition {
    if (!effect.clipId.trim()) throw new Error("Effect clipId is required.");
    const normalized = Object.freeze({ ...effect, order: Math.max(0, Math.floor(effect.order)), parameters: Object.freeze({ ...effect.parameters }) });
    this.effects.set(normalized.effectId, normalized);
    return normalized;
  }

  updateParameters(effectId: string, parameters: Readonly<Record<string, TimelineHistoryJsonValue>>): TimelineEffectDefinition {
    const effect = this.require(effectId);
    return this.upsertEffect({ ...effect, parameters: Object.freeze({ ...effect.parameters, ...parameters }) });
  }

  setEnabled(effectId: string, enabled: boolean): TimelineEffectDefinition {
    return this.upsertEffect({ ...this.require(effectId), enabled });
  }

  reorderEffect(effectId: string, order: number): readonly TimelineEffectDefinition[] {
    const target = this.require(effectId);
    const clipEffects = [...this.getEffects(target.clipId)].filter((item) => item.effectId !== effectId);
    clipEffects.splice(Math.max(0, Math.min(clipEffects.length, Math.floor(order))), 0, target);
    clipEffects.forEach((item, index) => this.upsertEffect({ ...item, order: index }));
    return this.getEffects(target.clipId);
  }

  removeEffect(effectId: string): boolean { return this.effects.delete(effectId); }

  getEffects(clipId?: string, enabledOnly = false): readonly TimelineEffectDefinition[] {
    return Object.freeze([...this.effects.values()]
      .filter((item) => (!clipId || item.clipId === clipId) && (!enabledOnly || item.enabled))
      .sort((left, right) => left.order - right.order || left.effectId.localeCompare(right.effectId)));
  }

  restore(effects: readonly TimelineEffectDefinition[]): void {
    this.effects.clear();
    for (const effect of effects) this.upsertEffect(effect);
  }

  private require(effectId: string): TimelineEffectDefinition {
    const effect = this.effects.get(effectId);
    if (!effect) throw new Error(`Unknown effect: ${effectId}`);
    return effect;
  }
}
