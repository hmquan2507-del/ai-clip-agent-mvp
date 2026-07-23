import type {
  TimelineHistoryJsonValue,
} from "../contracts/timeline-history-contracts";
import type {
  TimelineHistoryKeyboardConfiguration,
  TimelineHistoryKeyboardEventLike,
} from "../contracts/timeline-history-integration-contracts";
import { TimelineHistoryIntegrationRuntime } from "./timeline-history-integration-runtime";

function isEditableTarget(target: EventTarget | null | undefined): boolean {
  if (!target || typeof target !== "object") return false;
  const candidate = target as { tagName?: string; isContentEditable?: boolean };
  const tag = candidate.tagName?.toLowerCase();
  return candidate.isContentEditable === true || tag === "input" || tag === "textarea" || tag === "select";
}

export class TimelineHistoryKeyboardIntegration<TState = TimelineHistoryJsonValue> {
  private readonly allowInEditableTargets: boolean;
  private readonly useMetaKey: boolean;
  private readonly useControlKey: boolean;

  constructor(
    private readonly integration: TimelineHistoryIntegrationRuntime<TState>,
    configuration: TimelineHistoryKeyboardConfiguration = {},
  ) {
    this.allowInEditableTargets = configuration.allowInEditableTargets ?? false;
    this.useMetaKey = configuration.useMetaKey ?? true;
    this.useControlKey = configuration.useControlKey ?? true;
  }

  async handleKeyDown(event: TimelineHistoryKeyboardEventLike): Promise<boolean> {
    if (!this.allowInEditableTargets && isEditableTarget(event.target)) return false;
    if (event.altKey || event.key.toLowerCase() !== "z") return false;
    const modifier = (this.useControlKey && event.ctrlKey) || (this.useMetaKey && event.metaKey);
    if (!modifier) return false;
    const snapshot = this.integration.getSnapshot();
    const redo = Boolean(event.shiftKey);
    if ((redo && !snapshot.canRedo) || (!redo && !snapshot.canUndo)) return false;
    event.preventDefault();
    const result = redo ? await this.integration.redo("keyboard") : await this.integration.undo("keyboard");
    return result.completed;
  }
}
