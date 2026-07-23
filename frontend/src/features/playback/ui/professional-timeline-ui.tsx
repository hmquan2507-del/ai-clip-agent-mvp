"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type KeyboardEvent as ReactKeyboardEvent,
  type PointerEvent as ReactPointerEvent,
} from "react";

import type {
  TimelineUiIntegrationController,
  TimelineUiIntegrationSnapshot,
  TimelineUiTool,
} from "../contracts/professional-timeline-ui-integration-contracts";
import type { TimelineKeyboardUiBridge } from "../runtime/timeline-keyboard-ui-bridge";

export interface ProfessionalTimelineUiProps {
  readonly controller: TimelineUiIntegrationController;
  readonly keyboardBridge: TimelineKeyboardUiBridge;
  readonly className?: string;
  readonly height?: number;
}

function useTimelineSnapshot(
  controller: TimelineUiIntegrationController,
): TimelineUiIntegrationSnapshot {
  const [snapshot, setSnapshot] = useState(
    controller.getSnapshot(),
  );

  useEffect(() => {
    const interval = window.setInterval(() => {
      setSnapshot(controller.getSnapshot());
    }, 50);

    return () => window.clearInterval(interval);
  }, [controller]);

  return snapshot;
}

const TOOLS: readonly {
  readonly id: TimelineUiTool;
  readonly label: string;
  readonly shortcut: string;
}[] = [
  { id: "select", label: "Select", shortcut: "V" },
  { id: "blade", label: "Blade", shortcut: "Ctrl+K" },
  { id: "trim", label: "Trim", shortcut: "T" },
  { id: "hand", label: "Hand", shortcut: "H" },
  { id: "slip", label: "Slip", shortcut: "Y" },
  { id: "slide", label: "Slide", shortcut: "U" },
];

export function ProfessionalTimelineUi({
  controller,
  keyboardBridge,
  className,
  height = 360,
}: ProfessionalTimelineUiProps) {
  const snapshot = useTimelineSnapshot(controller);
  const [paletteQuery, setPaletteQuery] = useState("");

  const tracks = useMemo(
    () =>
      snapshot.document.tracks.map((track) => ({
        track,
        clips: snapshot.document.clips.filter(
          (clip) => clip.trackId === track.id,
        ),
      })),
    [snapshot.document],
  );

  const refresh = useCallback(() => {
    setPaletteQuery((value) => value);
  }, []);

  const onKeyboard = useCallback(
    (event: ReactKeyboardEvent<HTMLDivElement>) => {
      if (snapshot.keyboard.disposed) return;

      const runtimeResult = keyboardBridge.dispatch(
        {
          key: event.key,
          ctrlKey: event.ctrlKey,
          shiftKey: event.shiftKey,
          altKey: event.altKey,
          metaKey: event.metaKey,
          repeat: event.repeat,
        },
        { playheadFrame: snapshot.playheadFrame },
      );

      if (runtimeResult?.preventDefault) {
        event.preventDefault();
      }
      refresh();
    },
    [keyboardBridge, refresh, snapshot],
  );

  const onTimelinePointerDown = (
    event: ReactPointerEvent<HTMLDivElement>,
  ) => {
    event.currentTarget.setPointerCapture(event.pointerId);
    controller.pointerDown({
      pointerId: event.pointerId,
      x: event.nativeEvent.offsetX,
      mode: snapshot.tool === "hand" ? "scrub" : "marquee",
    });
    refresh();
  };

  const onTimelinePointerMove = (
    event: ReactPointerEvent<HTMLDivElement>,
  ) => {
    controller.pointerMove({
      pointerId: event.pointerId,
      x: event.nativeEvent.offsetX,
      snapFrames: snapshot.document.clips.flatMap((clip) => [
        clip.startFrame,
        clip.endFrame,
      ]),
    });
    refresh();
  };

  const onTimelinePointerUp = (
    event: ReactPointerEvent<HTMLDivElement>,
  ) => {
    controller.pointerUp({
      pointerId: event.pointerId,
      commit: true,
    });
    refresh();
  };

  return (
    <section
      className={className}
      data-testid="professional-timeline-ui"
      tabIndex={0}
      onKeyDown={onKeyboard}
      style={{
        display: "grid",
        gridTemplateRows: "44px 1fr",
        minHeight: height,
        border: "1px solid rgba(255,255,255,0.12)",
        borderRadius: 12,
        overflow: "hidden",
        background: "#111317",
        color: "#f6f7f9",
        outline: "none",
      }}
    >
      <header
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          padding: "0 10px",
          borderBottom: "1px solid rgba(255,255,255,0.10)",
          background: "#171a20",
        }}
      >
        {TOOLS.map((tool) => (
          <button
            key={tool.id}
            type="button"
            title={`${tool.label} (${tool.shortcut})`}
            aria-pressed={snapshot.tool === tool.id}
            onClick={() => {
              controller.setTool(tool.id);
              refresh();
            }}
          >
            {tool.label}
          </button>
        ))}

        <span style={{ width: 1, height: 20, background: "#343842" }} />

        <button
          type="button"
          disabled={!snapshot.canUndo}
          onClick={() => {
            controller.undo();
            refresh();
          }}
        >
          Undo
        </button>
        <button
          type="button"
          disabled={!snapshot.canRedo}
          onClick={() => {
            controller.redo();
            refresh();
          }}
        >
          Redo
        </button>
        <button
          type="button"
          onClick={() => {
            controller.splitAtPlayhead();
            refresh();
          }}
        >
          Split
        </button>
        <button
          type="button"
          onClick={() => {
            controller.openCommandPalette();
            refresh();
          }}
        >
          Commands
        </button>

        <div style={{ marginLeft: "auto", fontVariantNumeric: "tabular-nums" }}>
          Frame {snapshot.playheadFrame}
        </div>
      </header>

      <div
        style={{
          position: "relative",
          overflow: "hidden",
          userSelect: "none",
        }}
        onPointerDown={onTimelinePointerDown}
        onPointerMove={onTimelinePointerMove}
        onPointerUp={onTimelinePointerUp}
        onPointerCancel={() => controller.cancelPointer()}
        onContextMenu={(event) => {
          event.preventDefault();
          controller.openContextMenu(
            event.clientX,
            event.clientY,
          );
          refresh();
        }}
      >
        <div
          aria-hidden="true"
          style={{
            position: "absolute",
            inset: 0,
            backgroundImage:
              "linear-gradient(to right, rgba(255,255,255,0.06) 1px, transparent 1px)",
            backgroundSize: `${Math.max(8, snapshot.viewport.pixelsPerFrame * 10)}px 100%`,
          }}
        />

        {tracks.map(({ track, clips }, trackIndex) => (
          <div
            key={track.id}
            data-track-id={track.id}
            style={{
              position: "relative",
              height: 72,
              borderBottom: "1px solid rgba(255,255,255,0.08)",
              background:
                trackIndex % 2 === 0
                  ? "rgba(255,255,255,0.01)"
                  : "rgba(255,255,255,0.025)",
            }}
          >
            <div
              style={{
                position: "absolute",
                left: 8,
                top: 7,
                zIndex: 2,
                fontSize: 11,
                opacity: 0.65,
              }}
            >
              {track.id}
            </div>

            {clips.map((clip) => {
              const left = controller.frameToPixel(clip.startFrame);
              const width = Math.max(
                2,
                controller.frameToPixel(clip.endFrame) - left,
              );
              const selected =
                snapshot.document.selection.includes(clip.id);

              return (
                <button
                  key={clip.id}
                  type="button"
                  data-clip-id={clip.id}
                  aria-selected={selected}
                  onClick={(event) => {
                    event.stopPropagation();
                    controller.selectClip(clip.id, {
                      toggle: event.ctrlKey || event.metaKey,
                      additive: event.shiftKey,
                    });
                    refresh();
                  }}
                  onPointerDown={(event) => {
                    event.stopPropagation();
                    event.currentTarget.setPointerCapture(
                      event.pointerId,
                    );
                    controller.pointerDown({
                      pointerId: event.pointerId,
                      x: event.clientX,
                      clipIds: [clip.id],
                      mode: snapshot.tool === "trim"
                        ? "trim-end"
                        : "move",
                    });
                  }}
                  onPointerMove={(event) => {
                    event.stopPropagation();
                    controller.pointerMove({
                      pointerId: event.pointerId,
                      x: event.clientX,
                      snapFrames: snapshot.document.clips.flatMap(
                        (candidate) => [
                          candidate.startFrame,
                          candidate.endFrame,
                        ],
                      ),
                    });
                  }}
                  onPointerUp={(event) => {
                    event.stopPropagation();
                    controller.pointerUp({
                      pointerId: event.pointerId,
                    });
                    refresh();
                  }}
                  style={{
                    position: "absolute",
                    left,
                    top: 24,
                    width,
                    height: 38,
                    overflow: "hidden",
                    borderRadius: 7,
                    border: selected
                      ? "2px solid #ffffff"
                      : "1px solid rgba(255,255,255,0.22)",
                    background: selected ? "#3c475d" : "#29313f",
                    color: "#fff",
                    textAlign: "left",
                    padding: "0 9px",
                    cursor:
                      snapshot.tool === "trim"
                        ? "ew-resize"
                        : "grab",
                  }}
                >
                  {clip.id}
                </button>
              );
            })}
          </div>
        ))}

        <div
          aria-label="Playhead"
          style={{
            position: "absolute",
            top: 0,
            bottom: 0,
            left: controller.frameToPixel(snapshot.playheadFrame),
            width: 2,
            background: "#fff",
            pointerEvents: "none",
          }}
        />

        {snapshot.snapGuide?.visible ? (
          <div
            aria-label={snapshot.snapGuide.label}
            style={{
              position: "absolute",
              top: 0,
              bottom: 0,
              left: snapshot.snapGuide.x,
              width: 1,
              background: "#f3f4f6",
              pointerEvents: "none",
            }}
          />
        ) : null}

        {snapshot.contextMenu.open ? (
          <div
            role="menu"
            style={{
              position: "fixed",
              left: snapshot.contextMenu.x,
              top: snapshot.contextMenu.y,
              zIndex: 50,
              display: "grid",
              gap: 4,
              width: 180,
              padding: 8,
              borderRadius: 9,
              background: "#1c2028",
              boxShadow: "0 12px 40px rgba(0,0,0,0.42)",
            }}
          >
            <button type="button" onClick={() => controller.splitAtPlayhead()}>
              Split
            </button>
            <button type="button" onClick={() => controller.duplicateSelection(10)}>
              Duplicate
            </button>
            <button type="button" onClick={() => controller.deleteSelection(false)}>
              Delete
            </button>
            <button type="button" onClick={() => controller.deleteSelection(true)}>
              Ripple delete
            </button>
            <button type="button" onClick={() => controller.closeContextMenu()}>
              Close
            </button>
          </div>
        ) : null}

        {snapshot.commandPaletteOpen ? (
          <div
            role="dialog"
            aria-label="Timeline command palette"
            style={{
              position: "absolute",
              left: "50%",
              top: 18,
              zIndex: 60,
              width: 420,
              maxWidth: "90%",
              transform: "translateX(-50%)",
              padding: 12,
              borderRadius: 12,
              background: "#1b1f27",
              boxShadow: "0 18px 60px rgba(0,0,0,0.5)",
            }}
          >
            <input
              autoFocus
              value={paletteQuery}
              placeholder="Search commands"
              onChange={(event) => setPaletteQuery(event.target.value)}
              style={{ width: "100%" }}
            />
            <button
              type="button"
              onClick={() => {
                controller.closeCommandPalette();
                refresh();
              }}
            >
              Close
            </button>
          </div>
        ) : null}
      </div>
    </section>
  );
}
