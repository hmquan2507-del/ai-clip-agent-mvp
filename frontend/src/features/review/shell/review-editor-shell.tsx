import { ReviewEditorSurface } from "../design-system";
import { ReviewEditorRail } from "./editor-rail";
import { ReviewEditorTopbar } from "./editor-topbar";
import { ReviewAICommandBar } from "./ai-command-bar";
import { ReviewTimelinePanel } from "./timeline";
import { ReviewInspectorPanel, ReviewPreviewStage } from "./workspace-panels";
import type { ReviewEditorViewModel } from "../integration/contracts";

export interface ReviewEditorShellProps {
  view?: ReviewEditorViewModel;
  refreshing?: boolean;
  onRefresh?: () => void;
}

export function ReviewEditorShell({
  view,
  refreshing = false,
  onRefresh,
}: ReviewEditorShellProps) {
  return (
    <ReviewEditorSurface className="flex h-dvh min-h-[620px] flex-col overflow-hidden">
      <ReviewEditorTopbar
        view={view?.header}
        refreshing={refreshing}
        onRefresh={onRefresh}
      />

      <div className="grid min-h-0 flex-1 grid-cols-[64px_minmax(0,1fr)_300px] max-xl:grid-cols-[58px_minmax(0,1fr)] max-md:grid-cols-1">
        <ReviewEditorRail />
        <ReviewPreviewStage view={view?.preview} />
        <ReviewInspectorPanel view={view?.inspector} />
      </div>

      <ReviewTimelinePanel view={view?.timeline} />
      <ReviewAICommandBar disabled={Boolean(view)} />
    </ReviewEditorSurface>
  );
}
