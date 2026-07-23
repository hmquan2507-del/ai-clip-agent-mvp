import type { TimelineHistoryJsonValue } from "../contracts/timeline-history-contracts";
import { TimelineHistoryIntegrationRuntime } from "./timeline-history-integration-runtime";

export interface TimelineHistoryWorkspaceSessionConfiguration {
  readonly restoreOnAttach?: boolean;
  readonly persistOnDetach?: boolean;
}

export class TimelineHistoryWorkspaceSessionBridge<TState = TimelineHistoryJsonValue> {
  private attached = false;
  private readonly restoreOnAttach: boolean;
  private readonly persistOnDetach: boolean;

  constructor(
    private readonly integration: TimelineHistoryIntegrationRuntime<TState>,
    configuration: TimelineHistoryWorkspaceSessionConfiguration = {},
  ) {
    this.restoreOnAttach = configuration.restoreOnAttach ?? true;
    this.persistOnDetach = configuration.persistOnDetach ?? true;
  }

  async attach(): Promise<boolean> {
    if (this.attached) return false;
    this.attached = true;
    if (this.restoreOnAttach && await this.integration.loadWorkspace()) return true;
    if (!this.integration.getSnapshot().initialized) await this.integration.initialize();
    return true;
  }

  async detach(): Promise<boolean> {
    if (!this.attached) return false;
    if (this.persistOnDetach && this.integration.getSnapshot().initialized) await this.integration.saveWorkspace();
    this.attached = false;
    return true;
  }

  isAttached(): boolean { return this.attached; }
}
