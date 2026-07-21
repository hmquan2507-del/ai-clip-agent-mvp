"use client";

import type {
  RefObject,
  WheelEvent as ReactWheelEvent,
} from "react";
import {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  createReviewTimelineViewportRuntime,
} from "./factory";
import type {
  ReviewTimelineViewportState,
} from "./contracts";

export interface UseReviewTimelineViewportInput {
  duration: number;
  scrollRef: RefObject<HTMLDivElement | null>;
  labelsRef: RefObject<HTMLDivElement | null>;
}

export interface ReviewTimelineViewportController {
  state: ReviewTimelineViewportState;
  zoomIn(): void;
  zoomOut(): void;
  fit(): void;
  synchronizeScroll(): void;
  zoomAtPointer(
    event: ReactWheelEvent<HTMLDivElement>,
  ): void;
}

export function useReviewTimelineViewport({
  duration,
  scrollRef,
  labelsRef,
}: UseReviewTimelineViewportInput):
ReviewTimelineViewportController {
  const [runtime] = useState(
    () =>
      createReviewTimelineViewportRuntime(),
  );
  const [state, setState] =
    useState<ReviewTimelineViewportState>(
      () => runtime.getState(),
    );

  useEffect(
    () =>
      runtime.subscribe((nextState) => {
        setState(nextState);
      }),
    [runtime],
  );

  useEffect(() => {
    const scrollElement = scrollRef.current;
    if (!scrollElement) return;

    const synchronize = () => {
      const labelsWidth =
        labelsRef.current
          ?.getBoundingClientRect().width ?? 112;
      const viewportWidth = Math.max(
        1,
        scrollElement.clientWidth - labelsWidth,
      );

      runtime.synchronize({
        duration,
        viewportWidth,
        baseContentWidth: Math.max(
          620,
          viewportWidth,
        ),
      });
    };

    synchronize();
    const observer = new ResizeObserver(
      synchronize,
    );
    observer.observe(scrollElement);

    return () => observer.disconnect();
  }, [duration, labelsRef, runtime, scrollRef]);

  useEffect(() => {
    const element = scrollRef.current;
    if (
      element &&
      Math.abs(
        element.scrollLeft - state.scrollLeft,
      ) > 0.5
    ) {
      element.scrollLeft = state.scrollLeft;
    }
  }, [scrollRef, state.scrollLeft]);

  useEffect(() => {
    return () => {
      runtime.dispose();
    };
  }, [runtime]);

  const synchronizeScroll = useCallback(() => {
    const scrollLeft =
      scrollRef.current?.scrollLeft ?? 0;
    if (
      Math.abs(scrollLeft - state.scrollLeft) > 0.5
    ) {
      runtime.setScrollLeft(scrollLeft);
    }
  }, [runtime, scrollRef, state.scrollLeft]);

  const zoomAtPointer = useCallback(
    (event: ReactWheelEvent<HTMLDivElement>) => {
      if (!event.ctrlKey && !event.metaKey) return;
      event.preventDefault();
      const element = scrollRef.current;
      const labels = labelsRef.current;
      if (!element || !labels) return;

      const rect = element.getBoundingClientRect();
      const labelsWidth =
        labels.getBoundingClientRect().width;
      const offset = Math.min(
        state.viewportWidth,
        Math.max(
          0,
          event.clientX - rect.left - labelsWidth,
        ),
      );
      const anchorTime =
        state.duration <= 0
          ? 0
          : (
              state.scrollLeft + offset
            ) /
            state.contentWidth *
            state.duration;

      runtime.setZoom(
        state.zoom +
          (event.deltaY < 0 ? 0.5 : -0.5),
        anchorTime,
        offset,
      );
    },
    [labelsRef, runtime, scrollRef, state],
  );

  return {
    state,
    zoomIn: () => {
      runtime.zoomIn();
    },
    zoomOut: () => {
      runtime.zoomOut();
    },
    fit: () => {
      runtime.fit();
    },
    synchronizeScroll,
    zoomAtPointer,
  };
}
