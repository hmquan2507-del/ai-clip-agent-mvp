import { AISuggestions } from "./ai-suggestions";
import { ReviewSidebar } from "./review-sidebar";
import { SubtitlePreview } from "./subtitle-preview";
import { TranscriptPanel } from "./transcript-panel";
import { VideoPreviewPanel } from "./video-preview-panel";

export function ReviewWorkspace() {
  return (
    <section className="grid gap-6 xl:grid-cols-[1.35fr_0.75fr]">
      <div className="grid gap-6">
        <VideoPreviewPanel />

        <div className="grid gap-6 2xl:grid-cols-2">
          <TranscriptPanel />
          <SubtitlePreview />
        </div>
      </div>

      <div className="grid gap-6">
        <ReviewSidebar />
        <AISuggestions />
      </div>
    </section>
  );
}
