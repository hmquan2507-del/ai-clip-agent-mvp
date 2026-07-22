import type {
  TimelineHistoryBranch,
  TimelineHistoryEntry,
  TimelineHistoryJsonValue,
  TimelineUndoRedoHistorySnapshot,
} from "../contracts/timeline-history-contracts";

export interface TimelineHistoryBranchLineage {
  readonly branchId: string;
  readonly lineage: readonly string[];
  readonly depth: number;
  readonly rootBranchId: string;
}

export interface TimelineHistoryBranchSwitchPlan<TState = TimelineHistoryJsonValue> {
  readonly switchable: boolean;
  readonly fromBranchId: string;
  readonly toBranchId: string;
  readonly commonAncestorBranchId: string | null;
  readonly commonEntryId: string | null;
  readonly undoEntries: readonly TimelineHistoryEntry<TState>[];
  readonly redoEntryIds: readonly string[];
  readonly reason: string;
}

const freezeBranch = (branch: TimelineHistoryBranch): TimelineHistoryBranch =>
  Object.freeze({ ...branch, entryIds: Object.freeze([...branch.entryIds]) });

export class TimelineHistoryBranchManager<TState = TimelineHistoryJsonValue> {
  private readonly branches = new Map<string, TimelineHistoryBranch>();
  private readonly entries = new Map<string, TimelineHistoryEntry<TState>>();
  private activeBranchId = "main";

  synchronize(snapshot: TimelineUndoRedoHistorySnapshot<TState>): void {
    this.branches.clear();
    this.entries.clear();
    for (const branch of snapshot.branches) this.branches.set(branch.branchId, freezeBranch(branch));
    for (const entry of [...snapshot.past, ...snapshot.future]) this.entries.set(entry.entryId, entry);
    this.activeBranchId = snapshot.activeBranchId;
  }

  getActiveBranch(): TimelineHistoryBranch | null {
    return this.getBranch(this.activeBranchId);
  }

  getBranch(branchId: string): TimelineHistoryBranch | null {
    const branch = this.branches.get(branchId);
    return branch ? freezeBranch(branch) : null;
  }

  listBranches(): readonly TimelineHistoryBranch[] {
    return Object.freeze([...this.branches.values()].map(freezeBranch));
  }

  getLineage(branchId: string): TimelineHistoryBranchLineage | null {
    if (!this.branches.has(branchId)) return null;
    const lineage: string[] = [];
    const visited = new Set<string>();
    let cursor: string | null = branchId;
    while (cursor) {
      if (visited.has(cursor)) throw new Error(`Timeline history branch cycle detected at ${cursor}.`);
      visited.add(cursor);
      lineage.push(cursor);
      cursor = this.branches.get(cursor)?.parentBranchId ?? null;
    }
    return Object.freeze({
      branchId,
      lineage: Object.freeze(lineage),
      depth: Math.max(0, lineage.length - 1),
      rootBranchId: lineage.at(-1) ?? branchId,
    });
  }

  findCommonAncestorBranch(leftBranchId: string, rightBranchId: string): string | null {
    const left = this.getLineage(leftBranchId);
    const right = this.getLineage(rightBranchId);
    if (!left || !right) return null;
    const rightSet = new Set(right.lineage);
    return left.lineage.find((branchId) => rightSet.has(branchId)) ?? null;
  }

  planSwitch(targetBranchId: string): TimelineHistoryBranchSwitchPlan<TState> {
    const source = this.branches.get(this.activeBranchId);
    const target = this.branches.get(targetBranchId);
    if (!source || !target) {
      return Object.freeze({
        switchable: false,
        fromBranchId: this.activeBranchId,
        toBranchId: targetBranchId,
        commonAncestorBranchId: null,
        commonEntryId: null,
        undoEntries: Object.freeze([]),
        redoEntryIds: Object.freeze([]),
        reason: "branch-not-found",
      });
    }
    if (source.branchId === target.branchId) {
      return Object.freeze({
        switchable: true,
        fromBranchId: source.branchId,
        toBranchId: target.branchId,
        commonAncestorBranchId: source.branchId,
        commonEntryId: source.entryIds.at(-1) ?? null,
        undoEntries: Object.freeze([]),
        redoEntryIds: Object.freeze([]),
        reason: "already-active",
      });
    }
    const commonAncestorBranchId = this.findCommonAncestorBranch(source.branchId, target.branchId);
    const commonEntryId = this.findLastCommonEntry(source.entryIds, target.entryIds);
    const commonIndex = commonEntryId ? source.entryIds.lastIndexOf(commonEntryId) : -1;
    const undoEntries = source.entryIds
      .slice(commonIndex + 1)
      .reverse()
      .map((entryId) => this.entries.get(entryId))
      .filter((entry): entry is TimelineHistoryEntry<TState> => Boolean(entry));
    const targetCommonIndex = commonEntryId ? target.entryIds.lastIndexOf(commonEntryId) : -1;
    const redoEntryIds = target.entryIds.slice(targetCommonIndex + 1);
    return Object.freeze({
      switchable: commonAncestorBranchId !== null,
      fromBranchId: source.branchId,
      toBranchId: target.branchId,
      commonAncestorBranchId,
      commonEntryId,
      undoEntries: Object.freeze(undoEntries),
      redoEntryIds: Object.freeze(redoEntryIds),
      reason: commonAncestorBranchId ? "switch-plan-ready" : "branches-unrelated",
    });
  }

  private findLastCommonEntry(left: readonly string[], right: readonly string[]): string | null {
    const rightSet = new Set(right);
    for (let index = left.length - 1; index >= 0; index -= 1) {
      if (rightSet.has(left[index])) return left[index];
    }
    return null;
  }
}
