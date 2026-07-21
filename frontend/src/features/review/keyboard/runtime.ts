import {
  REVIEW_TIMELINE_KEYBOARD_CONTRACT_VERSION,
  type ReviewTimelineKeyboardContext,
  type ReviewTimelineKeyboardInput,
  type ReviewTimelineKeyboardResult,
  type ReviewTimelineKeyboardRuntimeListener,
  type ReviewTimelineKeyboardRuntimeState,
} from "./contracts";
import {
  identifyReviewTimelineKeyboardShortcut,
  resolveReviewTimelineKeyboardShortcut,
} from "./resolver";

const INITIAL_STATE: ReviewTimelineKeyboardRuntimeState = {
  contractVersion:
    REVIEW_TIMELINE_KEYBOARD_CONTRACT_VERSION,
  activeShortcut: null,
  lastIntent: null,
  lastResult: null,
  handledCount: 0,
  stateRevision: 0,
  updatedAt: null,
};

export interface ReviewTimelineKeyboardRuntimeOptions {
  now?: () => string;
}

export class ReviewTimelineKeyboardShortcutRuntime {
  private state = clone(INITIAL_STATE);
  private readonly listeners =
    new Set<ReviewTimelineKeyboardRuntimeListener>();
  private readonly now: () => string;
  private disposed = false;

  constructor(
    options: ReviewTimelineKeyboardRuntimeOptions = {},
  ) {
    this.now =
      options.now ??
      (() => new Date().toISOString());
  }

  getState(): ReviewTimelineKeyboardRuntimeState {
    return clone(this.state);
  }

  subscribe(
    listener: ReviewTimelineKeyboardRuntimeListener,
  ): () => void {
    this.assertNotDisposed();
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }

  handleKeyDown(
    input: ReviewTimelineKeyboardInput,
    context: ReviewTimelineKeyboardContext,
  ): ReviewTimelineKeyboardResult {
    this.assertNotDisposed();

    let result =
      resolveReviewTimelineKeyboardShortcut(
        input,
        context,
      );
    const shortcut =
      identifyReviewTimelineKeyboardShortcut(
        input,
        context.platform,
      );

    if (
      result.handled &&
      shortcut &&
      this.state.activeShortcut?.chord ===
        shortcut.chord
    ) {
      result = {
        ...result,
        handled: false,
        intent: null,
        blockedReason:
          "shortcut_already_active",
      };
    }

    const handledCount =
      this.state.handledCount +
      (result.handled ? 1 : 0);

    this.patchState({
      activeShortcut:
        result.handled && shortcut
          ? shortcut
          : this.state.activeShortcut,
      lastIntent:
        result.intent ?? this.state.lastIntent,
      lastResult: result,
      handledCount,
    });

    return clone(result);
  }

  handleKeyUp(
    input: ReviewTimelineKeyboardInput,
  ): ReviewTimelineKeyboardRuntimeState {
    this.assertNotDisposed();
    const active = this.state.activeShortcut;
    const key = input.key.trim().toLowerCase();

    if (
      active &&
      active.triggerKey === key
    ) {
      this.patchState({
        activeShortcut: null,
      });
    }

    return this.getState();
  }

  reset(): ReviewTimelineKeyboardRuntimeState {
    this.assertNotDisposed();
    this.replaceState({
      ...INITIAL_STATE,
      stateRevision:
        this.state.stateRevision + 1,
      updatedAt: this.now(),
    });
    return this.getState();
  }

  dispose(): void {
    if (this.disposed) return;
    this.listeners.clear();
    this.state = {
      ...this.state,
      activeShortcut: null,
      stateRevision:
        this.state.stateRevision + 1,
      updatedAt: this.now(),
    };
    this.disposed = true;
  }

  private patchState(
    patch: Partial<ReviewTimelineKeyboardRuntimeState>,
  ): void {
    this.replaceState({
      ...this.state,
      ...clone(patch),
      stateRevision:
        this.state.stateRevision + 1,
      updatedAt: this.now(),
    });
  }

  private replaceState(
    state: ReviewTimelineKeyboardRuntimeState,
  ): void {
    const previousState = clone(this.state);
    this.state = clone(state);
    for (const listener of this.listeners) {
      listener(
        clone(this.state),
        clone(previousState),
      );
    }
  }

  private assertNotDisposed(): void {
    if (this.disposed) {
      throw new Error(
        "Timeline keyboard shortcut runtime is disposed.",
      );
    }
  }
}

function clone<T>(value: T): T {
  return structuredClone(value);
}
