"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
  type RefObject,
} from "react";

/**
 * The real Timeline Runtime (`ReviewTimelinePanel`) owns its own zoom/scroll
 * state internally (one fresh instance per mount, no exported store, no prop
 * for it — confirmed by reading `features/review/viewport/` and
 * `features/review/shell/timeline.tsx`). There is no supported way to
 * subscribe to it without editing that file, which this sprint must not do.
 *
 * What IS safe, read-only, and requires zero edits to the runtime:
 *   - The scroll container DOM node exposes `data-review-timeline-zoom`
 *     (mutates on every zoom change) and is itself a real scrollable element
 *     (`scrollLeft`/`scrollWidth`/`clientWidth` are native DOM properties).
 *   - `playheadTime`, `revision`, and selected clip ids are already plain
 *     data in the view-model prop that flows into both `ReviewTimelinePanel`
 *     and this app's own components — no DOM access needed for those.
 *
 * This context is the seam: it observes the real timeline's DOM node
 * (attribute + native scroll/resize) for zoom/scroll, and receives
 * playhead/revision/selection as ordinary props (same source of truth the
 * real timeline itself reads from) — see the sprint report for the full
 * tradeoff writeup.
 */
export interface TimelineViewportValue {
  pixelsPerSecond: number;
  scrollLeft: number;
  timelineWidth: number;
  visibleRange: { startTime: number; endTime: number };
  zoomLevel: number;
  playheadTime: number;
  duration: number;
  revision: number;
  selection: Set<string>;
  observedContainerRef: RefObject<HTMLDivElement | null>;
  setScrollLeft: (next: number) => void;
  /** True once the real timeline's scroll container has been found and is being observed. */
  connected: boolean;
}

const TimelineViewportContext = createContext<TimelineViewportValue | null>(null);

export function useTimelineViewportContext(): TimelineViewportValue {
  const value = useContext(TimelineViewportContext);
  if (!value) {
    throw new Error("useTimelineViewportContext must be used within a TimelineViewportProvider");
  }
  return value;
}

export interface TimelineViewportProviderProps {
  duration: number;
  playheadTime: number;
  revision: number;
  selectedClipIds: readonly string[];
  children: ReactNode;
}

const REAL_TIMELINE_SCROLL_SELECTOR = "[data-review-timeline-scroll]";

export function TimelineViewportProvider({
  duration,
  playheadTime,
  revision,
  selectedClipIds,
  children,
}: TimelineViewportProviderProps) {
  const observedContainerRef = useRef<HTMLDivElement | null>(null);
  const realNodeRef = useRef<HTMLElement | null>(null);
  const relayingRef = useRef(false);

  const [scrollLeft, setScrollLeftState] = useState(0);
  const [timelineWidth, setTimelineWidth] = useState(0);
  const [contentWidth, setContentWidth] = useState(0);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const root = observedContainerRef.current;
    if (!root) return undefined;

    let raf = 0;
    let disposed = false;

    const readGeometry = () => {
      const node = realNodeRef.current;
      if (!node) return;
      setTimelineWidth(node.clientWidth);
      setContentWidth(node.scrollWidth);
      setScrollLeftState(node.scrollLeft);
      const zoomAttr = node.getAttribute("data-review-timeline-zoom");
      const parsedZoom = zoomAttr ? Number.parseFloat(zoomAttr) : NaN;
      setZoomLevel(Number.isFinite(parsedZoom) ? parsedZoom : 1);
    };

    const scheduleRead = () => {
      if (raf) return;
      raf = requestAnimationFrame(() => {
        raf = 0;
        if (!disposed) readGeometry();
      });
    };

    const attachToNode = (node: HTMLElement) => {
      realNodeRef.current = node;
      setConnected(true);
      readGeometry();

      node.addEventListener("scroll", scheduleRead, { passive: true });

      const mutationObserver = new MutationObserver(scheduleRead);
      mutationObserver.observe(node, { attributes: true, attributeFilter: ["data-review-timeline-zoom"] });

      const resizeObserver = new ResizeObserver(scheduleRead);
      resizeObserver.observe(node);

      return () => {
        node.removeEventListener("scroll", scheduleRead);
        mutationObserver.disconnect();
        resizeObserver.disconnect();
      };
    };

    // The real timeline mounts asynchronously (session must open first), so
    // poll briefly for its scroll container before giving up for this pass.
    let cleanupNode: (() => void) | null = null;
    let pollAttempts = 0;
    const pollInterval = window.setInterval(() => {
      pollAttempts += 1;
      const node = root.querySelector<HTMLElement>(REAL_TIMELINE_SCROLL_SELECTOR);
      if (node) {
        window.clearInterval(pollInterval);
        cleanupNode = attachToNode(node);
      } else if (pollAttempts > 100) {
        window.clearInterval(pollInterval);
      }
    }, 100);

    return () => {
      disposed = true;
      window.clearInterval(pollInterval);
      if (raf) cancelAnimationFrame(raf);
      cleanupNode?.();
    };
  }, []);

  const pixelsPerSecond = duration > 0 && contentWidth > 0 ? contentWidth / duration : 0;

  const visibleRange = useMemo(() => {
    if (pixelsPerSecond <= 0) return { startTime: 0, endTime: duration };
    return {
      startTime: scrollLeft / pixelsPerSecond,
      endTime: (scrollLeft + timelineWidth) / pixelsPerSecond,
    };
  }, [scrollLeft, timelineWidth, pixelsPerSecond, duration]);

  const setScrollLeft = useCallback((next: number) => {
    const node = realNodeRef.current;
    relayingRef.current = true;
    if (node && Math.abs(node.scrollLeft - next) > 0.5) {
      node.scrollLeft = next;
    }
    setScrollLeftState(next);
    relayingRef.current = false;
  }, []);

  const selection = useMemo(() => new Set(selectedClipIds), [selectedClipIds]);

  const value = useMemo<TimelineViewportValue>(
    () => ({
      pixelsPerSecond,
      scrollLeft,
      timelineWidth,
      visibleRange,
      zoomLevel,
      playheadTime,
      duration,
      revision,
      selection,
      observedContainerRef,
      setScrollLeft,
      connected,
    }),
    [
      pixelsPerSecond,
      scrollLeft,
      timelineWidth,
      visibleRange,
      zoomLevel,
      playheadTime,
      duration,
      revision,
      selection,
      setScrollLeft,
      connected,
    ],
  );

  return <TimelineViewportContext.Provider value={value}>{children}</TimelineViewportContext.Provider>;
}

/**
 * Wraps the real `ReviewTimelinePanel` so the provider can find and observe
 * its scroll container. This is the only "hook" into the real timeline — a
 * ref on a wrapper `div`, not an edit to any runtime file.
 */
export function TimelineViewportObservedRegion({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  const { observedContainerRef } = useTimelineViewportContext();
  return (
    <div ref={observedContainerRef} className={className}>
      {children}
    </div>
  );
}
