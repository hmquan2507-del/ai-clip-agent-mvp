import type { TimelineTransitionDefinition, TimelineTransitionEvaluation } from "../contracts/timeline-effects-animation-contracts";

const clamp01 = (value: number) => Math.max(0, Math.min(1, value));

export class TimelineTransitionRuntime {
  private readonly transitions = new Map<string, TimelineTransitionDefinition>();

  addTransition(transition: TimelineTransitionDefinition): TimelineTransitionDefinition {
    if (this.transitions.has(transition.transitionId)) throw new Error(`Transition already exists: ${transition.transitionId}`);
    if (transition.fromClipId === transition.toClipId) throw new Error("Transition requires two different clips.");
    if (!Number.isFinite(transition.startSeconds) || transition.startSeconds < 0) throw new Error("Transition start must be finite and non-negative.");
    if (!Number.isFinite(transition.durationSeconds) || transition.durationSeconds <= 0) throw new Error("Transition duration must be greater than zero.");
    const normalized = Object.freeze({ ...transition, parameters: Object.freeze({ ...transition.parameters }) });
    this.transitions.set(normalized.transitionId, normalized);
    return normalized;
  }

  updateTransition(transitionId: string, patch: Partial<Omit<TimelineTransitionDefinition, "transitionId">>): TimelineTransitionDefinition {
    const current = this.require(transitionId);
    this.transitions.delete(transitionId);
    return this.addTransition({ ...current, ...patch, transitionId });
  }

  removeTransition(transitionId: string): boolean { return this.transitions.delete(transitionId); }

  getTransitions(clipId?: string): readonly TimelineTransitionDefinition[] {
    return Object.freeze([...this.transitions.values()]
      .filter((item) => !clipId || item.fromClipId === clipId || item.toClipId === clipId)
      .sort((left, right) => left.startSeconds - right.startSeconds));
  }

  evaluate(timeSeconds: number, clipId?: string): readonly TimelineTransitionEvaluation[] {
    return Object.freeze(this.getTransitions(clipId).map((transition) => {
      const raw = (timeSeconds - transition.startSeconds) / transition.durationSeconds;
      const progress = clamp01(raw);
      const active = transition.enabled && raw >= 0 && raw <= 1;
      return Object.freeze({ transitionId: transition.transitionId, active, progress, fromOpacity: 1 - progress, toOpacity: progress });
    }));
  }

  restore(transitions: readonly TimelineTransitionDefinition[]): void {
    this.transitions.clear();
    for (const transition of transitions) this.addTransition(transition);
  }

  private require(transitionId: string): TimelineTransitionDefinition {
    const transition = this.transitions.get(transitionId);
    if (!transition) throw new Error(`Unknown transition: ${transitionId}`);
    return transition;
  }
}
