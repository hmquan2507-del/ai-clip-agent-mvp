import { TIMELINE_EFFECTS_ANIMATION_CONTRACT_VERSION, type TimelineAnimatableProperty, type TimelineEffectsAnimationFrame, type TimelineEffectsAnimationSnapshot, type TimelineEffectDefinition, type TimelineKeyframe, type TimelineTransitionDefinition } from "../contracts/timeline-effects-animation-contracts";
import { TimelineAnimationTrackRuntime } from "./timeline-animation-track-runtime";
import { TimelineEffectStackRuntime } from "./timeline-effect-stack-runtime";
import { TimelineMotionPresetRegistry } from "./timeline-motion-preset-registry";
import { TimelineTransitionRuntime } from "./timeline-transition-runtime";

export class TimelineEffectsAnimationRuntime {
  readonly animation = new TimelineAnimationTrackRuntime();
  readonly effects = new TimelineEffectStackRuntime();
  readonly transitions = new TimelineTransitionRuntime();
  readonly presets = new TimelineMotionPresetRegistry();
  private version = 0;

  addKeyframe(keyframe: TimelineKeyframe): TimelineKeyframe { const result = this.animation.addKeyframe(keyframe); this.version += 1; return result; }
  addEffect(effect: TimelineEffectDefinition): TimelineEffectDefinition { const result = this.effects.addEffect(effect); this.version += 1; return result; }
  addTransition(transition: TimelineTransitionDefinition): TimelineTransitionDefinition { const result = this.transitions.addTransition(transition); this.version += 1; return result; }
  removeKeyframe(keyframeId: string): boolean { const removed = this.animation.removeKeyframe(keyframeId); if (removed) this.version += 1; return removed; }
  updateEffectParameters(effectId: string, parameters: TimelineEffectDefinition["parameters"]): TimelineEffectDefinition { const result = this.effects.updateParameters(effectId, parameters); this.version += 1; return result; }
  setEffectEnabled(effectId: string, enabled: boolean): TimelineEffectDefinition { const result = this.effects.setEnabled(effectId, enabled); this.version += 1; return result; }
  removeEffect(effectId: string): boolean { const removed = this.effects.removeEffect(effectId); if (removed) this.version += 1; return removed; }
  removeTransition(transitionId: string): boolean { const removed = this.transitions.removeTransition(transitionId); if (removed) this.version += 1; return removed; }

  applyPreset(presetId: string, clipId: string, startSeconds = 0, idFactory?: () => string): readonly TimelineKeyframe[] {
    const keyframes = this.presets.instantiate(presetId, clipId, startSeconds, idFactory);
    keyframes.forEach((keyframe) => this.animation.addKeyframe(keyframe));
    this.version += 1;
    return keyframes;
  }

  evaluateFrame(clipId: string, timeSeconds: number): TimelineEffectsAnimationFrame {
    const evaluated = this.animation.evaluateClip(clipId, timeSeconds);
    const properties: Partial<Record<TimelineAnimatableProperty, number>> = {};
    for (const item of evaluated) properties[item.property] = item.value;
    return Object.freeze({
      clipId,
      timeSeconds,
      properties: Object.freeze(properties),
      evaluated,
      effects: this.effects.getEffects(clipId, true),
      transitions: this.transitions.evaluate(timeSeconds, clipId).filter((item) => item.active),
    });
  }

  getSnapshot(): TimelineEffectsAnimationSnapshot {
    return Object.freeze({
      contractVersion: TIMELINE_EFFECTS_ANIMATION_CONTRACT_VERSION,
      version: this.version,
      keyframes: this.animation.getKeyframes(),
      effects: this.effects.getEffects(),
      transitions: this.transitions.getTransitions(),
    });
  }

  restore(snapshot: TimelineEffectsAnimationSnapshot): void {
    if (snapshot.contractVersion !== TIMELINE_EFFECTS_ANIMATION_CONTRACT_VERSION) throw new Error("Unsupported timeline effects snapshot contract version.");
    this.animation.restore(snapshot.keyframes);
    this.effects.restore(snapshot.effects);
    this.transitions.restore(snapshot.transitions);
    this.version = snapshot.version + 1;
  }
}
