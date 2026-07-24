import { memo, type CSSProperties, type ReactNode } from "react";

export interface DesktopGridProps {
  toolRailWidth: number;
  assetLibraryWidth: number;
  inspectorWidth: number;
  timelineHeight: number;

  header: ReactNode;
  rail: ReactNode;
  assets: ReactNode;
  assetsDivider: ReactNode;
  preview: ReactNode;
  timelineDivider: ReactNode;
  timeline: ReactNode;
  inspectorDivider: ReactNode;
  inspector: ReactNode;
  statusBar: ReactNode;
}

const GRID_TEMPLATE_AREAS = [
  '"header      header  header  header  header  header"',
  '"rail        assets  divA    preview preview preview"',
  '"timelineDiv timelineDiv timelineDiv timelineDiv timelineDiv timelineDiv"',
  '"timeline    timeline timeline timeline divB    inspector"',
  '"status      status  status  status   status  status"',
].join(" ");

/**
 * The Desktop Editor's docking grid — a pure CSS Grid layout primitive.
 * Column/row *sizes* are driven by CSS custom properties (so resizing only
 * ever touches inline style values, not the grid structure), while the grid
 * *shape* (`grid-template-areas`) is a static constant. No editing/runtime
 * logic lives here — layout only.
 *
 * Memoized because panel content re-renders on every runtime tick (playhead,
 * pending states, etc.) far more often than the grid shape itself changes.
 */
function DesktopGridImpl({
  toolRailWidth,
  assetLibraryWidth,
  inspectorWidth,
  timelineHeight,
  header,
  rail,
  assets,
  assetsDivider,
  preview,
  timelineDivider,
  timeline,
  inspectorDivider,
  inspector,
  statusBar,
}: DesktopGridProps) {
  const style: CSSProperties & Record<string, string | number> = {
    display: "grid",
    gridTemplateAreas: GRID_TEMPLATE_AREAS,
    gridTemplateColumns: `${toolRailWidth}px ${assetLibraryWidth}px 6px minmax(0, 1fr) 6px ${inspectorWidth}px`,
    gridTemplateRows: `auto minmax(0, 1fr) 6px ${timelineHeight}px auto`,
    height: "100%",
    width: "100%",
  };

  return (
    <div className="desktop-editor-grid" style={style}>
      <div style={{ gridArea: "header" }} className="min-w-0">
        {header}
      </div>
      <div style={{ gridArea: "rail" }} className="min-h-0 min-w-0">
        {rail}
      </div>
      <div style={{ gridArea: "assets" }} className="min-h-0 min-w-0">
        {assets}
      </div>
      <div style={{ gridArea: "divA" }} className="min-h-0">
        {assetsDivider}
      </div>
      <div style={{ gridArea: "preview" }} className="min-h-0 min-w-0">
        {preview}
      </div>
      <div style={{ gridArea: "timelineDiv" }} className="min-w-0">
        {timelineDivider}
      </div>
      <div style={{ gridArea: "timeline" }} className="min-h-0 min-w-0">
        {timeline}
      </div>
      <div style={{ gridArea: "divB" }} className="min-h-0">
        {inspectorDivider}
      </div>
      <div style={{ gridArea: "inspector" }} className="min-h-0 min-w-0">
        {inspector}
      </div>
      <div style={{ gridArea: "status" }} className="min-w-0">
        {statusBar}
      </div>
    </div>
  );
}

export const DesktopGrid = memo(DesktopGridImpl);
