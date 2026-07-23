import type { TimelineHistoryJsonValue } from "../contracts/timeline-history-contracts";
import type { TimelineHistoryToolbarState } from "../contracts/timeline-history-integration-contracts";
import { TimelineHistoryIntegrationRuntime } from "./timeline-history-integration-runtime";

export class TimelineHistoryToolbarController<TState = TimelineHistoryJsonValue> {
  constructor(private readonly integration: TimelineHistoryIntegrationRuntime<TState>) {}

  getState(): TimelineHistoryToolbarState {
    const snapshot = this.integration.getSnapshot();
    return Object.freeze({
      canUndo: snapshot.canUndo,
      canRedo: snapshot.canRedo,
      undoLabel: snapshot.undoLabel,
      redoLabel: snapshot.redoLabel,
      busy: snapshot.busy,
    });
  }

  undo(): ReturnType<TimelineHistoryIntegrationRuntime<TState>["undo"]> {
    return this.integration.undo("toolbar");
  }

  redo(): ReturnType<TimelineHistoryIntegrationRuntime<TState>["redo"]> {
    return this.integration.redo("toolbar");
  }

  subscribe(listener: (state: TimelineHistoryToolbarState) => void): () => void {
    listener(this.getState());
    return this.integration.subscribe(() => listener(this.getState()));
  }
}
