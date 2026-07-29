import type { TimelineHistoryChange, TimelineHistoryJsonValue } from "../contracts/timeline-history-contracts";
import type { TimelineHistoryCommandResult } from "../contracts/timeline-history-integration-contracts";
import { TimelineHistoryIntegrationRuntime } from "./timeline-history-integration-runtime";

// eslint-disable-next-line @typescript-eslint/no-unused-vars -- TState is instantiated by callers (see TimelineEffectsHistoryBridge.execute below); not referenced within this interface's own fields.
export interface TimelineEffectsHistoryCommand<TState = TimelineHistoryJsonValue> {
  readonly commandId: string;
  readonly label: string;
  readonly mergeKey?: string | null;
  readonly metadata?: Readonly<Record<string, TimelineHistoryJsonValue>>;
  readonly changes: readonly TimelineHistoryChange[];
  execute(): void | Promise<void>;
}

export class TimelineEffectsHistoryBridge<TState = TimelineHistoryJsonValue> {
  constructor(private readonly history: TimelineHistoryIntegrationRuntime<TState>) {}

  execute(command: TimelineEffectsHistoryCommand<TState>): Promise<TimelineHistoryCommandResult<TState>> {
    return this.history.executeCommand({
      commandId: command.commandId,
      operation: "custom",
      label: command.label,
      sourceRuntime: "timeline-effects-animation-runtime",
      mergeKey: command.mergeKey ?? null,
      metadata: command.metadata,
      execute: async () => {
        await command.execute();
        return { changes: command.changes };
      },
    });
  }
}
